"""Dash components that provide preconfigured plots for visualizing data."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import dash_core_components as dcc
import plotly.express as px
import psutil

if TYPE_CHECKING:  # pragma: no cover
    from egon.pipeline import Pipeline


class CustomGraph(dcc.Graph):
    """The same as a Dash Graph instance but with modified default values

    Modified Defaults
        animate: True
        displayModeBar: False
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault('animate', True)
        kwargs.setdefault('config', dict())
        kwargs['config'].setdefault('displayModeBar', False)
        super().__init__(*args, **kwargs)


class CpuPercentageGraph(CustomGraph):
    """A graph representing the host system's CPU usage over time"""

    def __init__(self, *args, **kwargs) -> None:
        """Plot the percentage usage for each CPU core over time

        Args:
            Any arguments for a dash ``Graph`` object except ``figure``
        """

        cpu_labels = []
        plot_data = {'Time': [datetime.now()]}
        for i in range(psutil.cpu_count()):
            label = f'CPU{i}'
            cpu_labels.append(label)
            plot_data[label] = [0]

        fig = px.line(plot_data, x='Time', y=cpu_labels, labels={'value': 'CPU %'})
        fig.layout.update({'yaxis': {'range': [0, 100]}})
        super().__init__(*args, **kwargs, figure=fig)


class RamPercentageGraph(CustomGraph):
    """A graph representing the host system's RAM usage over time"""

    def __init__(self, *args, **kwargs) -> None:
        """Plot the percentage of RAM used over time

        Args:
            Any arguments for a dash ``Graph`` object except ``figure``
        """

        mem_usage_at_init = psutil.virtual_memory()[2]

        kwargs.setdefault('animate', True)
        fig = px.line({'Time': [datetime.now()], 'Memory (%)': [mem_usage_at_init]}, x='Time', y='Memory (%)')
        fig.layout.update({'yaxis': {'range': [0, 100]}})
        super().__init__(*args, **kwargs, figure=fig)


class PipelineQueueSize(CustomGraph):
    """A graph representing the number of queued objects in a pipeline"""

    def __init__(self, pipeline: Pipeline, *args, **kwargs) -> None:
        """Plot the size of a pipeline's input queues over time

        Args:
            Any arguments for a dash ``Graph`` object except ``figure``
        """

        node_labels = []
        plot_data = {'Time': [datetime.now()]}
        for input_connector in pipeline.connectors[0]:
            node_labels.append(input_connector.name)
            plot_data[input_connector.name] = [0]

        fig = px.line(plot_data, x='Time', y=node_labels, labels={'value': 'Queue Size'})
        super().__init__(*args, **kwargs, figure=fig)
