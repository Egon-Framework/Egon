"""Custom components that are highly specific to building Dash applications
for the Egon package.
"""

import dash_core_components as dcc
import dash_html_components as dhtml

DOC_URL = 'https://mwvgroup.github.io/Egon/'


class Logo(dhtml.Div):
    """The Egon application logo"""

    def __init__(self) -> None:
        super().__init__(className='div-logo', children=[
            dhtml.A(target=DOC_URL, className='display-inline', children=[
                # dhtml.Img(className='logo', src=self.get_asset_url('logo.svg')),
                dhtml.Span(className='logo-text', children=['Egon'])
            ])
        ])


class SummaryTable(dhtml.Div):
    """Summary table for pipeline metrics"""

    def __init__(self, pipeline) -> None:
        super().__init__(className='div-infotable', children=[
            dhtml.Table(id='table-pipeline-summary', children=[
                dhtml.Tr(children=[dhtml.Td(children=['Input Nodes']), dhtml.Td(children=['test1'])]),
                dhtml.Tr(children=[dhtml.Td(children=['Inline Nodes']), dhtml.Td(children=['test2'])]),
                dhtml.Tr(children=[dhtml.Td(children=['Target Nodes']), dhtml.Td(children=['test3'])]),
                dhtml.Tr(children=[dhtml.Td(children=['Total Nodes']), dhtml.Td(children=['test4'])]),
                dhtml.Tr(children=[dhtml.Td(children=['Connectors']), dhtml.Td(children=['test5'])])
            ])
        ])


class ClusterUsageWarning(dcc.Markdown):
    """Paragraph warning the user not to run on a cluster"""

    def __init__(self) -> None:
        super().__init__(
            'This interface provides a general overview of the current pipeline status. '
            'Please consult with a system administrator before running on a cluster environment. '
            f'For more information see the [official documentation]({DOC_URL}).'
        )
