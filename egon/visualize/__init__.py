"""Launches a web app for visualizing the status of a pipeline"""

import dash
import dash.dependencies as ddep
import dash_core_components as dcc
import dash_html_components as dhtml
import plotly.express as px

from egon.pipeline import Pipeline
from egon.visualize import callbacks
from egon.visualize import components as ecomp

DEFAULT_LAYOUT = 'grid'


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

        # self.callback(
        #     ddep.Output('pipeline-cyto', 'stylesheet'),
        #     ddep.Input('pipeline-cyto', 'pipeline_nodes'),
        #     ddep.Input('pipeline-cyto', 'n_intervals'),
        #     ddep.Input('interval', 'n_intervals')
        # )(callbacks.update_cytoscape_node_colors)

        self.callback(
            ddep.Output('graph-cpu-usage', 'extendData'), ddep.Input('interval', 'n_intervals')
        )(callbacks.get_cpu_usage)

        self.callback(
            ddep.Output('graph-mem-usage', 'extendData'), ddep.Input('interval', 'n_intervals')
        )(callbacks.get_memory_usage)

    def _build_html(self, pipeline: Pipeline, update_interval: int = 1) -> dhtml.Div:
        """Create the HTML content to be displayed by the app

        Args:
            pipeline: The pipeline to draw data from when populating the HTML
            update_interval: How frequently to update the page

        Returns:
            An HTML component
        """

        update_interval_ms = update_interval * 1000  # The interval in milliseconds
        page_update_interval = dcc.Interval(id='interval', interval=update_interval_ms)

        # The page has left and right columns which we build separately
        # Here we start building the left column
        left_column = \
            dhtml.Div(className='div-info three columns div-left-panel', children=[
                ecomp.custom.Logo(),
                ecomp.custom.ClusterUsageWarning(),
                dhtml.H6('Pipeline Summary'),
                ecomp.custom.SummaryTable(pipeline),
                dhtml.Div(className='div-run-button', children=[
                    dhtml.Button('Run Pipeline', id='run-button')
                ])
            ])

        # Here we start building the right column
        dropdown_layout_selector = \
            dcc.Dropdown(
                id='dropdown-layout',
                className='float-right',
                value=DEFAULT_LAYOUT,
                clearable=False,
                options=[{'label': name.title(), 'value': name} for name in ['grid', 'breadthfirst', 'circle']]
            )

        queue_data = {'Time': [0, 1], 'Queue Size': [0, 1], 'Node Name': [0, 1]}
        queue_fig = px.area(queue_data, x='Time', y='Queue Size')
        queue_graph = dcc.Graph(id='queue_size_plot', figure=queue_fig)

        right_column = \
            dhtml.Div(className='nine columns div-right-panel', children=[
                dropdown_layout_selector,
                ecomp.cyto.PipelineCytoscape(pipeline, id='pipeline-cyto'),
                dhtml.H4('Pipeline Load'),
                dhtml.Div(
                    className='div-pipeline-load',
                    children=[
                        queue_graph
                    ]),
                dhtml.H4('System Load'),
                dhtml.Div(
                    className='div-system-load',
                    children=[
                        ecomp.graphs.CpuPercentageGraph(id='graph-cpu-usage'),
                        ecomp.graphs.RamPercentageGraph(id='graph-mem-usage')
                    ]),
            ])

        # Return the fully assembled page with both columns
        return dhtml.Div(className='row', children=[left_column, right_column, page_update_interval])
