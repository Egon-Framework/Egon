"""Launches a Dash app for visualizing the status of a pipeline"""

from pathlib import Path
from typing import List

import dash
import dash_cytoscape as cyto
import dash_html_components as html
import yaml

from egon.nodes import AbstractNode, Source, Target
from egon.pipeline import Pipeline

DEFAULT_LAYOUT = 'breadthfirst'
STYLE_PATH = Path(__file__).resolve().parent / 'default_style.yml'


class PipelineCytoscape(cyto.Cytoscape):
    """A Dash compatible component for visualizing pipelines with cytoscape"""

    def __init__(self, app: dash.Dash, pipeline: Pipeline, **kwargs) -> None:
        """An interactive, cytoscape style plot of a constructed pipeline

        Args:
            app: The main application for handling event callbacks
            pipeline: The pipeline that will be visualized
            kwargs: Any additional ``Cytoscape`` arguments except for ``elements``
        """

        self._app = app
        self._pipeline = pipeline

        kwargs.setdefault('id', str(id(self)))
        stylesheet = kwargs.pop('stylesheet', self.default_stylesheet())

        # Useful docs: https://dash.plotly.com/cytoscape
        super().__init__(elements=self._get_pipeline_elements(), **kwargs)
        self.stylesheet = stylesheet

    def default_stylesheet(self) -> List[dict]:
        """Return a copy of the default style sheet

        Return:
            A list of style settings
        """

        with STYLE_PATH.open() as infile:
            return yaml.safe_load(infile)

    @staticmethod
    def node_class(node: AbstractNode) -> str:
        """Return the CSS class of a plotted node

        Return value depends on the type of node (e.g., source or target)

        Args:
            node: The node to return the class for

        Returns:
            The CSS class of the node
        """

        if isinstance(node, Source):
            return 'source_node'

        if isinstance(node, Target):
            return 'target_node'

        return 'default_node'

    def _get_pipeline_elements(self) -> List[dict]:
        """Return the pipeline elements to monitor"""

        # Iterate over pipeline nodes in an arbitrary order O(n)
        elements = []
        for node in self._pipeline.get_nodes():
            node_id = str(id(node))
            elements.append({
                'data': {'id': node_id, 'label': node.name},
                'classes': self.node_class(node)
            })

            # Draw an arrow from the node to any downstream nodes
            for downstream in node.downstream_nodes():
                downstream_id = str(id(downstream))
                elements.append(
                    {'data': {'source': node_id, 'target': downstream_id}}
                )

        return elements


class Visualizer(dash.Dash):
    """Application for visualizing an analysis pipeline"""

    def __init__(self, pipeline: Pipeline) -> None:
        """Create an interactive application for viewing pipeline objects

        Args:
            pipeline: The pipeline to build the application around
        """

        super().__init__(__name__)
        pipeline.validate()
        self.layout = self._build_html(pipeline)

    def _build_html(self, pipeline: Pipeline) -> dash.development.base_component.Component:
        """Create the HTML content to be displayed by the app

        Args:
            pipeline: The pipeline to draw data from when populating the HTML

        Returns:
            An HTML component
        """

        return html.Div([
            html.H1('Pipeline Overview', id='overview-header'),
            PipelineCytoscape(self, pipeline)
        ], id='overview-section')
