"""Launches a web app for visualizing the status of a pipeline"""

from pathlib import Path
from typing import List

import dash
import dash.dependencies as ddep
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as dhtml
import yaml

from egon.nodes import AbstractNode, Node, Source
from egon.pipeline import Pipeline

DEFAULT_LAYOUT = 'grid'
STYLE_PATH = Path(__file__).resolve().parent / 'assets' / 'default_style.yml'
DOC_URL = 'https://mwvgroup.github.io/Egon/'


class PipelineCytoscape(cyto.Cytoscape):
    """A Dash compatible component for visualizing pipelines with cytoscape"""

    def __init__(self, pipeline: Pipeline, **kwargs) -> None:
        """An interactive, cytoscape style plot of a constructed pipeline

        Args:
            pipeline: The pipeline that will be visualized
            kwargs: Any additional ``Cytoscape`` arguments except for ``elements``
        """

        elements = []
        self.pipeline_nodes = pipeline.get_nodes()
        stylesheet = kwargs.pop('stylesheet', self.default_stylesheet())

        # Iterate over pipeline nodes in an arbitrary order O(n)
        for node in pipeline.get_nodes():
            # Identify and label the node on the plot
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
    def node_class(node: AbstractNode) -> str:
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

    def _build_html(self, pipeline: Pipeline, update_interval: int = 2) -> dhtml.Div:
        """Create the HTML content to be displayed by the app

        Args:
            pipeline: The pipeline to draw data from when populating the HTML

        Returns:
            An HTML component
        """

        update_interval_ms = update_interval * 1000  # The interval in milliseconds
        cytoscape = PipelineCytoscape(pipeline, id='pipeline-cyto')

        @self.callback(ddep.Output('pipeline-cyto', 'stylesheet'), ddep.Input('interval', 'n_intervals'))
        def update_cytoscape_node_colors(*args) -> List[dict]:
            style = cytoscape.stylesheet
            for i, node in enumerate(cytoscape.pipeline_nodes):
                color = 'black' if node.node_finished else 'green'
                style[-i]['style']['background-color'] = color

            return style

        @self.callback(ddep.Output('pipeline-cyto', 'layout'), ddep.Input('dropdown-layout', 'value'))
        def update_layout(layout):
            return {'name': layout, 'animate': True}

        return dhtml.Div(
            className="row",
            children=[
                dhtml.Div(  # Left Panel Div
                    className="three columns div-left-panel",
                    children=[
                        dhtml.Div(  # Div for application info
                            className="div-info",
                            children=[
                                dhtml.A(
                                    target=DOC_URL,
                                    children=[
                                        dhtml.Img(className="logo", src=self.get_asset_url('logo.svg')),
                                        dhtml.Span(children=['Egon'], className='logo-text')
                                    ],
                                    className='display-inline'
                                ),
                                dcc.Markdown(
                                    'This interface provides a general overview of the current pipeline status. '
                                    'Please consult with a system administrator before running on a cluster enviornment. '
                                    f'For more information see the [official documentation]({DOC_URL}).'
                                ),
                                dhtml.H4('Pipeline Summary'),
                                dhtml.Button('Run Pipeline', id='run-button')
                            ],
                        ),
                    ],
                ),

                # Right Panel Div
                dhtml.Div(
                    className="nine columns div-right-panel",
                    children=[
                        dcc.Dropdown(
                            id='dropdown-layout',
                            value=DEFAULT_LAYOUT,
                            clearable=False,
                            options=[
                                {'label': name.capitalize(), 'value': name}
                                for name in ['grid', 'breadthfirst', 'circle']
                            ],
                            className='float-right'
                        ),
                        cytoscape,
                        dhtml.Div(
                            className="pipeline-load",
                            children=[
                                dhtml.H2('Pipeline Load')
                            ]
                        ),
                        dhtml.Div(
                            className="system-load",
                            children=[
                                dhtml.H2('System Load')
                            ]
                        )
                    ],
                ),
                dcc.Interval(id="interval", interval=update_interval_ms)
            ],
        )
