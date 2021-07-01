import math
import numpy
import os
import os.path
import ctypes
import tempfile
import shutil

StringLength = 1024


def getBooleanTagValue(modelObject, name):
    value = modelObject.tags.get(name, None)
    if value is None or value == 'False':
        return False
    elif value == 'True':
        return True
    else:
        raise Exception('Unrecognised value for {}: {}'.format(name, value))


class ActuatorState(object):

    def __init__(self, x, xdot, xdotdot):
        self.x = x
        self.xdot = xdot
        self.xdotdot = xdotdot


class Actuator(object):

    def __init__(self, omega, gamma, dt):
        self.omega = omega
        self.gamma = gamma
        self.dt = dt  # assumes contant time step
        self.uprev = 0.0
        # assume zero inital state (i.e. can not start from a half run sim)
        self.prevState = ActuatorState(0.0, 0.0, 0.0)
        beta = math.sqrt(1.0 - gamma**2)
        self.g = math.exp(-gamma * omega * dt) * math.sin(beta * omega * dt) / (beta * omega)
        self.f = math.exp(-gamma * omega * dt) * (gamma * math.sin(beta * omega * dt) / beta + math.cos(beta * omega * dt))

    def output(self, input):
        u = input
        f, g = self.f, self.g
        omegaSqr = self.omega**2
        gamma2Omega = 2.0 * self.gamma * self.omega
        xprev, xdotprev = self.prevState.x, self.prevState.xdot
        udot = (u - self.uprev) / self.dt
        state = ActuatorState(
            f * xprev + g * xdotprev + (2.0 * self.gamma * (f - 1.0) / self.omega + self.dt - g) * udot + (1.0 - f) * self.uprev,
            -g * omegaSqr * (xprev - self.uprev) + (f - gamma2Omega * g) * xdotprev + (1.0 - f) * udot,
            (gamma2Omega * g - f) * omegaSqr * (xprev - self.uprev) + ((4.0 * self.gamma**2 - 1.0) * omegaSqr * g - gamma2Omega * f) * xdotprev + omegaSqr * g * udot
        )
        self.prevState = state
        self.uprev = u
        return state.x, state.xdot, state.xdotdot


class BladedController(object):

    def __init__(self, info):
        info.CanResumeSimulation = False
        turbine = info.ModelObject
        model = info.Model
        modelDirectory = info.ModelDirectory
        #print(modelDirectory)
        
        self.periodNow = OrcFxAPI.Period(OrcFxAPI.pnInstantaneousValue)

        def checkInitialPitch(initialPitch):
            if initialPitch != 0.0:
                raise Exception(turbine.Name + ' initial blade pitch must be zero.')

        if turbine.DataNameValid('PitchControlMode'):  # if v11.0a or later
            checkInitialPitch(turbine.InitialPitch[0])
            #if turbine.PitchControlMode != 'Common':
            #    raise Exception(turbine.Name + ' must use common pitch control mode.')
        else:
            checkInitialPitch(turbine.InitialPitch)

        self.DLLCanBeShared = getBooleanTagValue(turbine, 'ControllerDLLCanBeShared')
        self.useActuator = getBooleanTagValue(turbine, 'UseActuator')
        self.setCWDToModelDir = getBooleanTagValue(turbine, 'SetCWDToModelDir')
        self.lastupdateTime = -numpy.inf
        self.firstCall = True
        self.simulationStartTime = model.simulationStartTime
        self.momentScaleFactor = turbine.UnitsConversionFactor('FF.LL')
        self.velocityScaleFactor = turbine.UnitsConversionFactor('LL.TT^-1')
        
        # Stephan
        self.filename = os.path.basename(info.ModelFileName)
        #Initiate debug file
        self.printContrDebugFile = getBooleanTagValue(turbine, 'PrintDebugFile')
        
        if self.printContrDebugFile:
            self.DebugFilename = os.path.splitext(info.ModelFileName)[0] + "_Debug.txt"
                
        self.IPC = turbine.PitchControlMode
        
        
        print(self.filename)

        ''' If setCWDToModelDir is true, set the current working directory to the model's directory.
            This can be useful if the controller dll uses the current working directory to read a 
            file from a relative file path.

            An example of this is the perf. file, used with the ROSCO control dll. In this case,
            setCWDToModelDir can be True and the perf. file placed in the model directory.

            HOWEVER, if running multiple simulations in batch, setCWDToModelDir should always be False. For the
            ROSCO control dll, a full absolute path could be given for the perf. file in the input file. '''
        if self.setCWDToModelDir:
            os.chdir(modelDirectory)

        if model.general.DynamicsSolutionMethod == 'Explicit time domain':
            self.dt = info.Model.general.ActualOuterTimeStep
        else:
            if model.general.ImplicitUseVariableTimeStep == 'No':
                self.dt = info.Model.general.ImplicitConstantTimeStep
            else:
                raise Exception('Wrapper only tested for constant timestep.')

        if self.useActuator:
            omega = float(turbine.tags.ActuatorOmega)
            gamma = float(turbine.tags.ActuatorGamma)
            self.actuator = Actuator(omega, gamma, self.dt)

        DLLfileName = os.path.join(modelDirectory, turbine.tags.ControllerDLL)
        if not self.DLLCanBeShared:
            with tempfile.NamedTemporaryFile(suffix='.dll', delete=False) as tmp:
                self.DLLfileName = tmp.name
            shutil.copy2(DLLfileName, self.DLLfileName)
            DLLfileName = self.DLLfileName

        try:
            # load with ctypes.windll.kernel32.LoadLibraryW so we can use ctypes.windll.kernel32.FreeLibrary before we del the DLL
            LoadLibrary = ctypes.windll.kernel32.LoadLibraryW
            LoadLibrary.restype = ctypes.c_void_p
            LoadLibrary.argtypes = (ctypes.c_wchar_p,)
            self.libHandle = LoadLibrary(DLLfileName)
            if self.libHandle is None:
                raise ctypes.WinError()

            self.dll = ctypes.CDLL('', handle=self.libHandle)
            self.DISCON = self.dll.DISCON
            self.DISCON.restype = None
            self.DISCON.argtypes = (
                OrcFxAPI.wrapped_ndpointer(dtype=numpy.float32, ndim=1, flags='C_CONTIGUOUS'),
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.c_char_p
            )

            self.avrSwap = numpy.zeros(84, numpy.float32)
            self.aviFail = ctypes.c_int()

            self.inputFileName = turbine.tags.get('InputFile', None)
            if self.inputFileName is None:
                self.accInfile = (ctypes.c_char * StringLength)()
            else:
                self.inputFileName = os.path.join(modelDirectory, turbine.tags.InputFile)
                self.accInfile = self.inputFileName.encode('utf-8')

            self.avcOutname = (ctypes.c_char * StringLength)()
            self.avcMsg = (ctypes.c_char * StringLength)()
        except BaseException:
            self.unloadDLL()
            raise

    def __del__(self):
        if not self.firstCall:
            self.finalise()
        self.unloadDLL()

    def unloadDLL(self):
        if self.libHandle is not None:
            FreeLibrary = ctypes.windll.kernel32.FreeLibrary
            FreeLibrary.restype = ctypes.c_bool
            FreeLibrary.argtypes = (ctypes.c_void_p,)
            FreeLibrary(self.libHandle)
        if not self.DLLCanBeShared:
            os.remove(self.DLLfileName)

    def getRecord(self, index):
        # convert between 1-based FORTRAN indexing and 0-based numpy indexing
        return self.avrSwap[index - 1]

    def setRecord(self, index, value):
        # convert between 1-based FORTRAN indexing and 0-based numpy indexing
        self.avrSwap[index - 1] = value

    def callDLL(self):
        self.DISCON(self.avrSwap, self.aviFail, self.accInfile, self.avcOutname, self.avcMsg)
        
        # print to external output
        #print(self.avrSwap)
        #print(self.aviFail)
        #print(self.accInfile)
        #print(self.avcOutname)
        #print(self.avcMsg)

        #print swap array to text file
        #print(self.DebugFilename)
        if self.printContrDebugFile:
            outF = open(self.DebugFilename, "a")
            outF.writelines('\t'.join(["{:.8e}".format(x) for x in self.avrSwap]) + '\n')
            outF.close()


    def update(self, info):
        if info.NewTimeStep and info.SimulationTime > self.lastupdateTime:
        
            self.lastupdateTime = info.SimulationTime

            turbine = info.ModelObject
            
            def deg2rad(deg):
            
                return deg / 180.0 * numpy.pi
            
            
            def IndividualBladePitch(blade_no):
            
                PitchAngle = info.ModelObject.TimeHistory(
                'Blade pitch',  # this OrcaFlex result is the angle we want
                self.periodNow,
                OrcFxAPI.oeTurbine(blade_no)
                )[0]  
                
                return deg2rad(PitchAngle)
                
            def IndividualRootBM(blade_no):
            
                RootBM = info.ModelObject.TimeHistory(
                'Root connection Ey moment',  # flapwise bending moment
                self.periodNow,
                OrcFxAPI.oeTurbine(blade_no)
                )[0] * 1000.  
                
                return abs(RootBM)

            # iStatus
            if self.firstCall:
                self.torque = 0.0
                self.setRecord(50, len(self.accInfile))
                self.setRecord(51, StringLength)
                self.setRecord(1, 0)
                self.firstCall = False
                
                # Write debug file header to avoid ressetting during extraction
                if self.printContrDebugFile:
                    header = []
                    for i in range(84):
                        tmp_str = "avrSwap[" + str(i+1) + "]"
                        header.append(tmp_str.ljust(15))
                    outF = open(self.DebugFilename, "w")
                    outF.writelines('\t'.join([x for x in header]) + '\n')
                    outF.close()
                
            else:
                self.setRecord(1, 1)

            # length of avcMsg character array
            self.setRecord(49, StringLength)

            # number of blades
            self.setRecord(61, info.InstantaneousCalculationData.BladeCount)

            # blade pitch            
            if self.IPC == "Common":
                pitch = info.InstantaneousCalculationData.BladePitchAngle
                self.setRecord(4, pitch)
                self.setRecord(33, pitch)
                self.setRecord(34, pitch)
                
            elif self.IPC == "Individual":
                #pitch = info.InstantaneousCalculationData.BladePitchAngle
                pitch = [IndividualBladePitch(1),IndividualBladePitch(2),IndividualBladePitch(3)]
                OutOfPlaneBM = [IndividualRootBM(1),IndividualRootBM(2),IndividualRootBM(3)]
                # Set pitch
                self.setRecord(4, pitch[0])
                self.setRecord(33, pitch[1])
                self.setRecord(34, pitch[2])
                # Set BM
                self.setRecord(30, OutOfPlaneBM[0])
                self.setRecord(31, OutOfPlaneBM[1])
                self.setRecord(32, OutOfPlaneBM[2])
                # Set to individual in controller
                self.setRecord(28, 1)
            

            # horizontal hub wind speed
            self.setRecord(27, info.InstantaneousCalculationData.HorizontalHubWindSpeed / self.velocityScaleFactor)

            # rotor azimuth angle
            self.setRecord(60, info.InstantaneousCalculationData.RotorAngle)

            # time
            self.setRecord(2, info.SimulationTime - self.simulationStartTime)

            # time step
            self.setRecord(3, self.dt)

           # generator speed
            self.setRecord(20, info.InstantaneousCalculationData.GeneratorAngVel)

            # rotor speed
            self.setRecord(21, info.InstantaneousCalculationData.MainShaftAngVel)

            # torque and power
            # DLL assumed to work in Nm
            dllTorque =-self.torque * 1000.000 / self.momentScaleFactor
            self.setRecord(23, dllTorque)
            self.setRecord(15, dllTorque * info.InstantaneousCalculationData.GeneratorAngVel) # power not factored by efficiency

            # "nodding" acceleration
            self.setRecord(83, -info.InstantaneousCalculationData.TurbineAngularAcceleration[1]) # -ve convert to FAST coordinate system
            
            # tower "forward-aft" acceleration
            self.setRecord(53, -info.InstantaneousCalculationData.TurbineAcceleration[2]) #  

            # call DISCON
            self.callDLL()

            if self.aviFail.value < 0:
                raise Exception('Call to DISCON failed')

            # read output from DISCON and assign state to be returned by external functions
            if self.useActuator:
                # Not adapted to individual blade pitch 
                self.pitch, self.pitchDot, self.pitchDotDot = self.actuator.output(self.getRecord(45))
            else:
                if self.IPC == "Common":
                    self.pitch = self.getRecord(45)
                    self.pitchDot = 0.0
                    self.pitchDotDot = 0.0
                elif self.IPC == "Individual":
                    #self.pitch = [self.getRecord(42) self.getRecord(43) self.getRecord(44)]
                    #self.pitch = self.getRecord(45)
                    self.pitch = []
                    self.pitch.append(self.getRecord(42))
                    self.pitch.append(self.getRecord(43))
                    self.pitch.append(self.getRecord(44))
                    #print(pitch)
                    self.pitchDot = 0.0
                    self.pitchDotDot = 0.0
            # DLL assumed to return value in Nm, first convert to OrcaFlex SI units (kN.m) and then to OrcaFlex model units
            self.torque = -self.getRecord(47) / 1000.0 * self.momentScaleFactor
            

    def finalise(self):
        # iStatus
        self.setRecord(1, -1)

        # call DISCON
        self.callDLL()
        



class BaseController(object):

    def Initialise(self, info):
        key = info.ModelObject.handle.value
        controller = info.Workspace.get(key, None)
        
        
        # Stephan          
        self.DebugFilename = os.path.splitext(info.ModelFileName)[0] + "_Debug.txt"
        
        if controller is None:
            controller = BladedController(info)
            info.Workspace[key] = controller
            
        self.controller = controller
        



    def Finalise(self, info):
        key = info.ModelObject.handle.value
        if key in info.Workspace:
            del(info.Workspace[key])
            

    def Calculate(self, info):
        
        # Write debug file header to avoid ressetting during extraction
       
        
        if (info.SimulationTime - info.Model.simulationStartTime) > 10.0:
            self.controller.update(info)
        else:
            self.controller.pitch = 0.0
            self.controller.pitchDot = 0.0
            self.controller.pitchDotDot = 0.0
            
            self.controller.torque = 0.0
        



class PitchController(BaseController):

    def Calculate(self, info):
        super().Calculate(info)
        #print(self.controller.pitch)
        if self.controller.IPC == "Common":
            info.StructValue.Value = self.controller.pitch
            info.StructValue.Velocity = self.controller.pitchDot
            info.StructValue.Acceleration = self.controller.pitchDotDot
        elif self.controller.IPC == "Individual":
            try:
                info.StructValue[0].Value = self.controller.pitch[0]
                info.StructValue[1].Value = self.controller.pitch[1]
                info.StructValue[2].Value = self.controller.pitch[2]
            except:
                info.StructValue[0].Value = 0.0
                info.StructValue[1].Value = 0.0
                info.StructValue[2].Value = 0.0        
        
        
        #info.StructValue.Velocity = self.controller.pitchDot
        #info.StructValue.Acceleration = self.controller.pitchDotDot


class TorqueController(BaseController):

    def Calculate(self, info):
        super().Calculate(info)
        info.Value = self.controller.torque
