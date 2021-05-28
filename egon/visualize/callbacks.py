"""Callbacks used to update the content of Dash components"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Tuple

import numpy as np
import psutil

if TYPE_CHECKING:  # pragma: no cover
    from egon.connectors import Input


def cast_layout_to_dict(layout: str) -> dict:
    """Return a cytoscape layout as a dictionary

    Args:
        layout: The layout of the cytoscape figure

    Returns:
        A dictionary for styling the cytoscape object
    """

    return {'name': layout, 'animate': True}


class BaseGraphCallback:
    """Base class for graph callbacks"""

    def __init__(self, max_data: Optional[int]) -> None:
        """A customized Dash graph

        Args:
            max_data: Maximum number of data points to display on the graph
        """

        self.max_data = max_data


class SystemUsage(BaseGraphCallback):
    """Callbacks for the current system usage"""

    # noinspection PyUnusedLocal
    def get_cpu_usage(self, *args: Optional) -> Tuple[dict, None, int]:
        """Return a dictionary with the current CPU usage

        Returns:
            A dictionary of CPU % usage formatted for use with plotly
        """

        now = datetime.now()
        y = np.transpose([psutil.cpu_percent(percpu=True)])
        x = np.full_like(y, now, dtype=datetime)
        return dict(x=x, y=y), None, self.max_data

    # noinspection PyUnusedLocal
    def get_memory_usage(self, *args: Optional) -> Tuple[dict, None, int]:
        """Return a dictionary with the current memory usage

        Returns:
            A dictionary of memory usage formatted for use with plotly
        """

        mem = psutil.virtual_memory()[2]
        return dict(x=[[datetime.now()]], y=[[mem]]), None, self.max_data


class PipelineStatus(BaseGraphCallback):
    """Callbacks for the status of a pipeline"""

    def __init__(self, max_data: int, connector_list: List[Input]):
        """A customized Dash graph

        Args:
            max_data: Maximum number of data points to display on the graph
            connector_list: A list of input connectors
        """

        super().__init__(max_data=max_data)
        self._connector_list = connector_list

    # noinspection PyUnusedLocal
    def get_queue_sizes(self, *args: Optional) -> Tuple[dict, None, int]:
        """Return a dictionary with the que size for a list of connectors

        Returns:
            A dictionary of queue sizes formatted for use with plotly
        """

        now = datetime.now()
        y = [[c.size()] for c in self._connector_list]
        x = np.full_like(y, now, dtype=datetime)
        return dict(x=x, y=y), None, self.max_data
