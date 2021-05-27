"""Launches a web app for visualizing the status of a pipeline"""

from functools import partial
from itertools import chain

import dash
import dash.dependencies as ddep
import dash_core_components as dcc
import dash_html_components as dhtml

from egon.pipeline import Pipeline
from egon.visualize import callbacks
from egon.visualize import components as ecomp

FORMAT_LABELS = ('Grid', 'Breadth First', 'Circle')
CYTOSCAPE_FORMATS = ('grid', 'breadthfirst', 'circle')
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

        self._pipeline = pipeline
        self.layout = self._build_html()
        self._assign_callbacks()
        self.title = 'Egon Visualizer'

    def _assign_callbacks(self) -> None:
        """Assign callbacks to connect templated HTML with pipeline behavior"""

        self.callback(
            ddep.Output('pipeline-cyto', 'layout'),
            ddep.Input('dropdown-layout', 'value')
        )(callbacks.cast_layout_to_dict)

        self.callback(
            ddep.Output('graph-queue-size', 'extendData'),
            ddep.Input('interval', 'n_intervals')
        )(partial(callbacks.get_queue_sizes, self._pipeline.connectors[0]))

        self.callback(
            ddep.Output('graph-cpu-usage', 'extendData'), ddep.Input('interval', 'n_intervals')
        )(callbacks.get_cpu_usage)

        self.callback(
            ddep.Output('graph-mem-usage', 'extendData'), ddep.Input('interval', 'n_intervals')
        )(callbacks.get_memory_usage)

    def _build_html(self, update_interval: int = 1) -> dhtml.Div:
        """Create the HTML content to be displayed by the app

        Args:
            update_interval: How frequently to update the page in milliseconds

        Returns:
            An HTML component
        """

        update_interval_ms = update_interval * 1000  # The interval in milliseconds
        page_update_interval = dcc.Interval(id='interval', interval=update_interval_ms)

        # The page has left and right columns which we build separately
        # Here we start building the left column
        left_column = \
            dhtml.Div(className='three columns div-left-panel', children=[
                ecomp.custom.Logo(),
                ecomp.custom.ClusterUsageWarning(),
                dhtml.H6('Pipeline Summary', id='h6-summary'),
                ecomp.custom.SummaryTable(self._pipeline)
            ])

        # Here we start building the right column
        dropdown_layout_selector = \
            dhtml.Div(className='div-dropdown-layout', children=[
                dcc.Dropdown(
                    id='dropdown-layout',
                    value=DEFAULT_LAYOUT,
                    clearable=False,
                    options=[{'label': label, 'value': name} for name, label in zip(CYTOSCAPE_FORMATS, FORMAT_LABELS)]
                )
            ])

        right_column = \
            dhtml.Div(className='nine columns div-right-panel', children=[
                dropdown_layout_selector,
                ecomp.cyto.PipelineCytoscape(self._pipeline, id='pipeline-cyto'),
                dhtml.H4('Pipeline Load'),
                dhtml.Div(
                    className='div-pipeline-load',
                    children=[
                        ecomp.graphs.PipelineQueueSize(self._pipeline, id='graph-queue-size')
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
