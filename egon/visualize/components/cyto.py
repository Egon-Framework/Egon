"""Dash components that provide a cytoscape-like representation of running
pipelines.
"""

from itertools import chain
from pathlib import Path
from typing import List

import dash_cytoscape as cyto
import yaml

from egon.connectors import Input, Output
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

        stylesheet = kwargs.pop('stylesheet', self.default_stylesheet())
        kwargs.setdefault('minZoom', 1)
        kwargs.setdefault('maxZoom', 1)

        elements = []
        for node in chain(*pipeline.nodes):
            # Identify and label the node on the plot
            node_id = str(id(node))
            elements.append({
                'data': {'id': node_id, 'label': node.name},
                'classes': self._get_classes(node)
            })

            for connector in chain(*node.connectors):
                connector_id = str(id(connector))
                elements.append({
                    'data': {'id': connector_id, 'parent': node_id, 'label': connector.name},
                    'classes': self._get_classes(connector)
                })

                if isinstance(connector, Input):
                    for partner in connector.get_partners():
                        partner_id = str(id(partner))
                        elements.append({
                            'data': {'source': partner_id,
                                     'source_label': partner.name,
                                     'target': connector_id,
                                     'target_label': connector.name}
                        })

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
    def _get_classes(node: AbstractNode) -> str:
        """Return the CSS class of a plotted node

        Return value depends on the type of node (e.g., source or target)

        Args:
            node: The node to return the class for

        Returns:
            The CSS class of the node
        """

        if isinstance(node, Input):
            return 'connector input'

        if isinstance(node, Output):
            return 'connector output'

        if isinstance(node, Node):
            return 'pipeline-node inline'

        if isinstance(node, Source):
            return 'pipeline-node source'

        return 'pipeline-node target'
