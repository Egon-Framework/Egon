"""Dash components that provide a cytoscape-like representation of running
pipelines.
"""

from pathlib import Path
from typing import List

import dash_cytoscape as cyto
import yaml

from egon.nodes import AbstractNode, Node, Source
from egon.pipeline import Pipeline

STYLE_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'default_style.yml'


class PipelineCytoscape(cyto.Cytoscape):
    """A Dash compatible component for visualizing pipelines with cytoscape"""

    def __init__(self, pipeline: Pipeline, **kwargs) -> None:
        """An interactive, cytoscape style plot of a constructed pipeline

        Args:
            pipeline: The pipeline that will be visualized
            kwargs: Any additional ``Cytoscape`` arguments except for ``elements``
        """

        elements = []
        stylesheet = kwargs.pop('stylesheet', self.default_stylesheet())

        # Iterate over pipeline nodes in an arbitrary order O(n)
        for node in pipeline.node_list:
            # Identify and label the node on the plot
            node_id = str(id(node))
            elements.append({
                'data': {'id': node_id, 'label': node.name},
                'classes': self._get_node_classes(node)
            })

            # Draw an arrow from the node to any downstream nodes
            for downstream in node.downstream_nodes():
                downstream_id = str(id(downstream))
                elements.append(
                    {'data': {'source': node_id, 'target': downstream_id}}
                )

            # Add individual CSS styling the current node
            # We guarantee that these values are at the end of the style sheet
            stylesheet.append(
                {
                    'selector': f'[id == {node_id}]',
                    'style': {
                        'background-color': 'grey'
                    }
                }
            )

        super().__init__(elements=elements, stylesheet=stylesheet, **kwargs)

    @staticmethod
    def default_stylesheet() -> List[dict]:
        """Return a copy of the default style sheet

        Return:
            A list of style settings
        """

        with STYLE_PATH.open() as infile:
            return yaml.safe_load(infile)

    @staticmethod
    def _get_node_classes(node: AbstractNode) -> str:
        """Return the CSS class of a plotted node

        Return value depends on the type of node (e.g., source or target)

        Args:
            node: The node to return the class for

        Returns:
            The CSS class of the node
        """

        if isinstance(node, Node):
            return 'default_node'

        if isinstance(node, Source):
            return 'source_node'

        return 'target_node'
