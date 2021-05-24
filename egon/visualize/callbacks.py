"""Callbacks used to update the content of Dash components"""

from time import time
from typing import List, Optional

import numpy as np
import psutil

from egon.connectors import Input


def cast_layout_to_dict(layout: str) -> dict:
    """Return a cytoscape layout as a dictionary

    Args:
        layout: The layout of the cytoscape figure

    Returns:
        A dictionary for styling the cytoscape object
    """

    return {'name': layout, 'animate': True}


def get_cytoscape_node_colors(pipeline_nodes: List, style: dict, *args: Optional) -> dict:
    """Return the color a pipeline's nodes should be shaded

    Args:
        pipeline_nodes: The nodes to return colors for
        style: The current styling of the pipeline nodes

    Returns:
        A dictionary for styling the node objects
    """

    style = style.copy()
    for i, node in enumerate(pipeline_nodes):
        color = 'grey' if node.node_finished else 'green'
        style[-i]['style']['background-color'] = color

    return style


def get_cpu_usage(*args) -> dict:
    """Return a dictionary with the current CPU usage

    Returns:
        A dictionary of CPU % usage formatted for use with plotly
    """

    now = time()
    y = np.transpose([psutil.cpu_percent(percpu=True)])
    x = np.full_like(y, now)
    return dict(x=x, y=y)


def get_memory_usage(*args) -> dict:
    """Return a dictionary with the current memory usage

    Returns:
        A dictionary of memory usage formatted for use with plotly
    """

    mem = psutil.virtual_memory()[2]
    return dict(x=[[time()]], y=[[mem]])


def get_queue_sizes(connector_list: List[Input], *args) -> dict:
    """Return a dictionary with the que size for a list of connectors

    Args:
        connector_list: A list of input connectors

    Returns:
        A dictionary of queue sizes formatted for use with plotly
    """

    now = time()
    y = [[c.size()] for c in connector_list]
    x = np.full_like(y, now)
    return dict(x=x, y=y)
