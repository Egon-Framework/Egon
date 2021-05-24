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
        inputs, outputs = pipeline.connectors
        number_inputs = len(inputs)
        number_outputs = len(outputs)
        total_connectors = number_inputs + number_outputs
        number_nodes = len(pipeline.node_list)

        super().__init__(className='div-infotable', children=[
            dhtml.Table(id='table-infotable', children=[
                dhtml.Tr(className='tr-property', children=[
                    dhtml.Td(className='td-property-name', children=['Total Nodes']),
                    dhtml.Td(className='td-property-value', children=[f'{number_nodes}'])]),
                dhtml.Tr(className='tr-sub-property', children=[
                    dhtml.Td(className='td-sub-property-name', children=['Source']),
                    dhtml.Td(className='td-sub-property-value', children=['test1'])]),
                dhtml.Tr(className='tr-sub-property', children=[
                    dhtml.Td(className='td-sub-property-name', children=['Inline']),
                    dhtml.Td(className='td-sub-property-value', children=['test2'])]),
                dhtml.Tr(className='tr-sub-property', children=[
                    dhtml.Td(className='td-sub-property-name', children=['Target']),
                    dhtml.Td(className='td-sub-property-value', children=['test3'])]),
                dhtml.Tr(className='tr-spacer', children=[]),
                dhtml.Tr(className='tr-property', children=[
                    dhtml.Td(className='td-property-name', children=['Total Connectors']),
                    dhtml.Td(className='td-property-value', children=[f'{total_connectors}'])]),
                dhtml.Tr(className='tr-sub-property', children=[
                    dhtml.Td(className='td-sub-property-name', children=['Inputs']),
                    dhtml.Td(className='td-sub-property-value', children=[f'{number_inputs}'])]),
                dhtml.Tr(className='tr-sub-property', children=[
                    dhtml.Td(className='td-sub-property-name', children=['Outputs']),
                    dhtml.Td(className='td-sub-property-value', children=[f'{number_outputs}'])])
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
