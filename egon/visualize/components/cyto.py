"""Dash components that provide a cytoscape-like representation of running
pipelines.
"""

from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import List, TYPE_CHECKING

import dash_cytoscape as cyto
import yaml

from egon.connectors import Input, Output
from egon.nodes import AbstractNode, Node, Source

if TYPE_CHECKING:  # pragma: no cover
    from egon.pipeline import Pipeline

STYLE_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'cyto_style.yml'


class PipelineCytoscape(cyto.Cytoscape):
    """A Dash compatible component for visualizing pipelines with cytoscape"""

    def __init__(self, pipeline: Pipeline, **kwargs) -> None:
        """An interactive, cytoscape style plot of a constructed pipeline

        If the ``stylesheet`` argument is provided, the default style sheet for
        this class is overwritten.

        Args:
            pipeline: The pipeline that will be visualized
            kwargs: Any additional ``Cytoscape`` arguments except for ``elements``
        """

        stylesheet = kwargs.pop('stylesheet', self.default_stylesheet())

        # Set customized defaults
        kwargs.setdefault('minZoom', 0.25)
        kwargs.setdefault('maxZoom', 2)
        kwargs.setdefault('style', dict())
        kwargs['style'].setdefault('width', '100%')
        kwargs['style'].setdefault('height', '800px')

        elements = []
        for node in chain(*pipeline.nodes):
            # Add the pipeline node to the figure
            node_id = str(id(node))
            elements.append({
                'data': {'id': node_id, 'label': node.name},
                'classes': self._get_classes(node)
            })

            for connector in chain(*node.connectors):
                # Add each connector to the figure
                connector_id = str(id(connector))
                elements.append({
                    'data': {'id': connector_id, 'parent': node_id, 'label': connector.name},
                    'classes': self._get_classes(connector)
                })

                # Draw an arrow between the connector and each of its partners
                if isinstance(connector, Input):
                    for partner in connector.partners:
                        partner_id = str(id(partner))
                        elements.append({
                            'data': {
                                'source': partner_id,
                                'source_label': partner.name,
                                'target': connector_id,
                                'target_label': connector.name
                            }
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
