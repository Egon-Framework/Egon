"""Launches a web app for visualizing the status of a pipeline"""

import dash
import dash.dependencies as ddep
import dash_core_components as dcc
import dash_html_components as dhtml

from egon.pipeline import Pipeline
from egon.visualize import callbacks
from egon.visualize.cyto import PipelineCytoscape

DEFAULT_LAYOUT = 'grid'
DOC_URL = 'https://mwvgroup.github.io/Egon/'


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
        self._assign_callbacks()

    def _assign_callbacks(self) -> None:
        """Assign callbacks to connect templated HTML with pipeline behavior"""

        self.callback(
            ddep.Output('pipeline-cyto', 'layout'),
            ddep.Input('dropdown-layout', 'value')
        )(callbacks.update_layout)

        self.callback(
            ddep.Output('pipeline-cyto', 'stylesheet'),
            ddep.Input('pipeline-cyto', 'pipeline_nodes'),
            ddep.Input('pipeline-cyto', 'n_intervals'),
            ddep.Input('interval', 'n_intervals')
        )(callbacks.update_cytoscape_node_colors)

    def _build_html(self, pipeline: Pipeline, update_interval: int = 2) -> dhtml.Div:
        """Create the HTML content to be displayed by the app

        Args:
            pipeline: The pipeline to draw data from when populating the HTML
            update_interval: How frequently to update the page

        Returns:
            An HTML component
        """

        update_interval_ms = update_interval * 1000  # The interval in milliseconds
        page_update_interval = dcc.Interval(id="interval", interval=update_interval_ms)

        # The page has left and right columns which we build separately
        # We define the contents of each column and then assemble them individually

        # Here we start building the left column
        # ######################################
        egon_logo = \
            dhtml.Div(className="div-logo", children=[
                dhtml.A(target=DOC_URL, className='display-inline', children=[
                    dhtml.Img(className="logo", src=self.get_asset_url('logo.svg')),
                    dhtml.Span(className='logo-text', children=['Egon'])
                ])
            ])

        pipeline_summary_table = \
            dhtml.Div(className="div-infotable", children=[
                dhtml.Table(children=[
                    dhtml.Tr(children=[dhtml.Td(children=['Input Nodes']), dhtml.Td(children=['test1'])]),
                    dhtml.Tr(children=[dhtml.Td(children=['Inline Nodes']), dhtml.Td(children=['test2'])]),
                    dhtml.Tr(children=[dhtml.Td(children=['Target Nodes']), dhtml.Td(children=['test3'])]),
                    dhtml.Tr(children=[dhtml.Td(children=['Total Nodes']), dhtml.Td(children=['test4'])]),
                    dhtml.Tr(children=[dhtml.Td(children=['Connectors']), dhtml.Td(children=['test5'])])
                ])
            ])

        pipeline_run_button = \
            dhtml.Div(className="div-runbutton", children=[
                dhtml.Button('Run Pipeline', id='run-button')
            ])

        lef_column = \
            dhtml.Div(className="div-info three columns div-left-panel", children=[
                egon_logo,
                dcc.Markdown(
                    'This interface provides a general overview of the current pipeline status. '
                    'Please consult with a system administrator before running on a cluster environment. '
                    f'For more information see the [official documentation]({DOC_URL}).'
                ),
                dhtml.H6('Pipeline Summary'),
                pipeline_summary_table,
                pipeline_run_button

            ])

        # Here we start building the right column
        # #######################################
        dropdown_layout_selector = \
            dcc.Dropdown(
                id='dropdown-layout',
                className='float-right',
                value=DEFAULT_LAYOUT,
                clearable=False,
                options=[{'label': name.title(), 'value': name} for name in ['grid', 'breadthfirst', 'circle']]
            )

        cytoscape = PipelineCytoscape(pipeline, id='pipeline-cyto')

        right_column = \
            dhtml.Div(className="nine columns div-right-panel", children=[
                dropdown_layout_selector,
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
            ])

        # Return the fully assembled page with both columns
        return dhtml.Div(className="row", children=[lef_column, right_column, page_update_interval])
