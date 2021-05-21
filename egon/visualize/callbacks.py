from typing import List, Optional


def update_layout(layout) -> dict:
    return {'name': layout, 'animate': True}


def update_cytoscape_node_colors(style: dict, pipeline_nodes: List, *args: Optional) -> List[dict]:
    for i, node in enumerate(pipeline_nodes):
        color = 'black' if node.node_finished else 'green'
        style[-i]['style']['background-color'] = color

    return style
