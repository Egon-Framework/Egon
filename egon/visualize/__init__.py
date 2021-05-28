"""Launches a web app for visualizing the status of a pipeline"""

from __future__ import annotations

from typing import TYPE_CHECKING

import dash
import dash.dependencies as ddep
import dash_core_components as dcc
import dash_html_components as dhtml

from egon.visualize import callbacks
from egon.visualize import components as ecomp

if TYPE_CHECKING:  # pragma: no cover
    from egon.pipeline import Pipeline

FORMAT_LABELS = ('Grid', 'Breadth First', 'Circle')
CYTOSCAPE_FORMATS = ('grid', 'breadthfirst', 'circle')
DEFAULT_LAYOUT = 'grid'


class Visualizer(dash.Dash):
    """Application for visualizing an analysis pipeline"""

    def __init__(self, pipeline: Pipeline, update_interval: int = 1, display_interval: int = 120) -> None:
        """Create an interactive application for viewing pipeline objects

        Args:
            pipeline: The pipeline to build the application around
        """

        pipeline.validate()

        self._pipeline = pipeline
        self._update_interval = update_interval
        self._num_displayed_data_points = display_interval // update_interval

        # self.layout = self._build_html()
        super().__init__(__name__, update_title=None, title='Egon Visualizer')
        self._assign_callbacks()

    def _assign_callbacks(self) -> None:
        """Assign callbacks to connect templated HTML with pipeline behavior"""

        self.callback(
            ddep.Output('pipeline-cyto', 'layout'),
            ddep.Input('dropdown-layout', 'value')
        )(callbacks.cast_layout_to_dict)

        pipeline_callbacks = callbacks.PipelineStatus(self._num_displayed_data_points, self._pipeline.connectors[0])
        self.callback(
            ddep.Output('graph-queue-size', 'extendData'),
            ddep.Input('interval', 'n_intervals')
        )(pipeline_callbacks.get_queue_sizes)

        system_callbacks = callbacks.SystemUsage(self._num_displayed_data_points)
        self.callback(
            ddep.Output('graph-cpu-usage', 'extendData'), ddep.Input('interval', 'n_intervals')
        )(system_callbacks.get_cpu_usage)

        self.callback(
            ddep.Output('graph-mem-usage', 'extendData'), ddep.Input('interval', 'n_intervals')
        )(system_callbacks.get_memory_usage)

    #################################################################################################
    # Some of the custom graph objects populate a placeholder value at init
    # By overwriting the _layout attribute, graphs are re-rendered every time the webpage refreshes.
    #################################################################################################

    @property
    def _layout(self) -> dhtml.Div:
        """Create the HTML content to be displayed by the app

        Returns:
            An HTML component
        """

        update_interval_ms = self._update_interval * 1000  # The interval in milliseconds
        page_update_interval = dcc.Interval(id='interval', interval=update_interval_ms)

        # The page has left and right columns which we build separately
        # Here we start building the left column
        left_column = \
            dhtml.Div(className='three columns div-left-panel', children=[
                ecomp.custom.Logo(),
                dcc.Markdown(
                    'This interface provides a general pipeline overview for testing and debugging purposes. '
                    'Please consult with a system administrator before running on a cluster environment. '
                    f'For more information see the [official documentation]({ecomp.custom.DOC_URL}).'
                ),
                dhtml.P(
                    'The structural preview of your pipeline will load with an automatically optimized '
                    'layout. Depending on the number of nodes in your pipeline and the size of your '
                    'window, you may need to manually reposition plot elements by dragging them around '
                    'the window. Predefined layouts are also provided via the dropdown box at the top '
                    'of the page.'
                ),
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

    @_layout.setter
    def _layout(self, x):
        pass
