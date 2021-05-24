"""Dash components that provide preconfigured plots for visualizing data."""

from time import time

import dash_core_components as dcc
import plotly.express as px
import psutil


class CpuPercentageGraph(dcc.Graph):
    """A graph representing the host system's CPU usage over time"""

    def __init__(self, *args, **kwargs) -> None:
        """Plot the percentage usage for each CPU core over time

        Args:
            Any arguments for a dash ``Graph`` object except ``figure``
        """

        cpu_labels = []
        plot_data = {'Time': [time()]}
        for i in range(psutil.cpu_count()):
            label = f'CPU{i}'
            cpu_labels.append(label)
            plot_data[label] = [0]

        kwargs.setdefault('animate', True)
        fig = px.line(plot_data, x='Time', y=cpu_labels)
        fig.layout.update({'yaxis': {'range': [0, 100]}})
        super().__init__(*args, **kwargs, figure=fig)


class RamPercentageGraph(dcc.Graph):
    """A graph representing the host system's RAM usage over time"""

    def __init__(self, *args, **kwargs) -> None:
        """Plot the percentage of RAM used over time

        Args:
            Any arguments for a dash ``Graph`` object except ``figure``
        """

        kwargs.setdefault('animate', True)
        mem_usage_at_init = psutil.virtual_memory()[2]

        fig = px.line({'Time': [time()], 'Memory (%)': [mem_usage_at_init]}, x='Time', y='Memory (%)')
        fig.layout.update({'yaxis': {'range': [0, 100]}})
        super().__init__(*args, **kwargs, figure=fig)
