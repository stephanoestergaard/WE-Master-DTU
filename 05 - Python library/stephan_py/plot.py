"""
This module contains plot functions used in the project
"""
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def BarPlot1Series(labels,series1,folder_prefix):

    # Plots bar plot comparing simulation series
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, series1, width, label='Series: ' + folder_prefix[0])
    #rects2 = ax.bar(x + width/2, series2, width, label='Series: ' + folder_prefix[1])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('DEL in parameter unit')
    ax.set_title('DEL')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    #ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def BarPlot2Series(labels,series1,series2,folder_prefix):

    # Plots bar plot comparing simulation series
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, series1, width, label='Series: ' + folder_prefix[0])
    rects2 = ax.bar(x + width/2, series2, width, label='Series: ' + folder_prefix[1])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('DEL in parameter unit')
    ax.set_title('DEL')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()
    
def BarPlotAEP2Series(labels,series1,series2,folder_prefix):   

    # Plots bar plot comparing simulation series
    
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, series1, width, label='Series: ' + folder_prefix[0])
    rects2 = ax.bar(x + width/2, series2, width, label='Series: ' + folder_prefix[1])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('AEP [GWh]')
    ax.set_title('AEP comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()
    
    
    
def Plot_TH_stats_traces(title, plot_series_x, plot_series_y, x_label, y_label, y_unit, series_names, modes, secondary_axis, n_rows = 1):

    # Plots X value series on the primary axis or on the secondary axis.

    fig = make_subplots(specs=[[{'secondary_y': True}]], rows = n_rows)

    # Add traces
    if isinstance(series_names, list):
        for i in range(len(plot_series_x)):
            fig.add_trace(go.Scatter(x=plot_series_x[i], y=plot_series_y[i],
                    mode=modes[i],
                    name=series_names[i]),
                    secondary_y=secondary_axis[i])
    else:
        fig.add_trace(go.Scatter(x=plot_series_x, y=plot_series_y,
                    mode=modes,
                    name=series_names),
                    secondary_y=secondary_axis)


    # Use date string to set xaxis range
    fig['layout']['yaxis2']['showgrid'] = False
    fig.update_layout(title_text=title, title_x=0.5)
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=y_label + ' [' + y_unit + ']', secondary_y=False)


    fig.show()
    
    return fig
    
    
    
def DecayPlot(title, series_names, plot_series_x, plot_series_y, y1_label, x2_label, tickvals):
    
    
    fig = make_subplots(rows = 2, cols = 1,
                   subplot_titles=(title,"Initial Cycle Amplitude vs Damping Ratio"))
    
    if not isinstance(series_names, list):
        # Upper plot
        fig.add_trace(go.Scatter(x=plot_series_x[0], y=plot_series_y[0],
            mode='lines',
            name=series_names),
            row = 1,
            col = 1
        )

        fig.add_trace(go.Scatter(x=plot_series_x[1], y=plot_series_y[1],
            mode='markers',
            name='Turn points'),
            row = 1,
            col = 1
        )
    
        # Lower plot
        fig.add_trace(go.Scatter(x=plot_series_x[2], y=plot_series_y[2],
            mode='lines+markers',
            name='Damp ratio'),
            row = 2,
            col = 1
        )
        
    elif isinstance(series_names, list):
        
        # Upper plot
        fig.add_trace(go.Scatter(x=plot_series_x[0], y=plot_series_y[0],
            mode='lines',
            name=series_names[0]),
            row = 1,
            col = 1
        )

        fig.add_trace(go.Scatter(x=plot_series_x[1], y=plot_series_y[1],
            mode='markers',
            name='Turn points'),
            row = 1,
            col = 1
        )
    
        # Lower plot
        fig.add_trace(go.Scatter(x=plot_series_x[2], y=plot_series_y[2],
            mode='lines+markers',
            name='Damp ratio'),
            row = 2,
            col = 1
        )
        
        
        # Upper plot
        fig.add_trace(go.Scatter(x=plot_series_x[3], y=plot_series_y[3],
            mode='lines',
            name=series_names[1]),
            row = 1,
            col = 1
        )

        fig.add_trace(go.Scatter(x=plot_series_x[4], y=plot_series_y[4],
            mode='markers',
            name='Turn points'),
            row = 1,
            col = 1
        )
    
        # Lower plot
        fig.add_trace(go.Scatter(x=plot_series_x[5], y=plot_series_y[5],
            mode='lines+markers',
            name='Damp ratio'),
            row = 2,
            col = 1
        )
    
    
    fig.update_xaxes(title_text='Time (s)',
                    row = 1,
                    rangemode = "tozero")
    fig.update_yaxes(title_text=y1_label,
                    row = 1,
                    tickvals = tickvals[0])
    
    
    fig.update_xaxes(title_text=x2_label,
                    row = 2)
    fig.update_yaxes(title_text='Damping ratio [%]',
                    row = 2,
                    tickvals = tickvals[1])
    

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='white')
    

    fig.show()
    
    
    