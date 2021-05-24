from time import time
from typing import List, Optional

import numpy as np
import psutil


def update_layout(layout) -> dict:
    return {'name': layout, 'animate': True}


def update_cytoscape_node_colors(style: dict, pipeline_nodes: List, *args: Optional) -> List[dict]:
    for i, node in enumerate(pipeline_nodes):
        color = 'black' if node.node_finished else 'green'
        style[-i]['style']['background-color'] = color

    return style


def get_cpu_usage(*args):
    now = time()
    y = np.transpose([psutil.cpu_percent(percpu=True)])
    x = list([now] for _ in range(psutil.cpu_count()))
    return dict(x=x, y=y), list(range(psutil.cpu_count()))


def get_memory_usage(*args):
    mem = psutil.virtual_memory()[2]
    return dict(x=[[time()]], y=[[mem]])
