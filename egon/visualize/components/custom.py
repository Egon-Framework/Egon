"""Custom Dash components that are highly specific to the Egon package."""

import dash_html_components as dhtml

DOC_URL = 'https://mwvgroup.github.io/Egon/'


class Logo(dhtml.Div):
    """The Egon application logo"""

    def __init__(self) -> None:
        super().__init__(className='div-logo', children=[
            dhtml.A(target=DOC_URL, className='display-inline', children=[
                dhtml.Img(className='logo', src='https://mwvgroup.github.io/Egon/assets/images/logo.svg'),
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

        sources, nodes, targets = pipeline.nodes
        num_sources = len(sources)
        num_nodes = len(nodes)
        num_targets = len(targets)
        number_nodes = num_sources + num_nodes + num_targets

        super().__init__(className='div-info-table', children=[
            dhtml.Table(className='table-info-primary', children=[
                dhtml.Tr(children=[
                    dhtml.Td(children=[f'Total Nodes: {number_nodes}'])]),
                dhtml.Tr(children=[
                    dhtml.Td(children=[
                        dhtml.Table(className='table-info-secondary', children=[
                            dhtml.Tr(children=[
                                dhtml.Td(children=['Source:']),
                                dhtml.Td(children=[f'{num_sources}'])]),
                            dhtml.Tr(children=[
                                dhtml.Td(children=['Inline:']),
                                dhtml.Td(children=[f'{num_nodes}'])]),
                            dhtml.Tr(children=[
                                dhtml.Td(children=['Target:']),
                                dhtml.Td(children=[f'{num_targets}'])
                            ])])])]),

                dhtml.Tr(children=[
                    dhtml.Td(children=[f'Total Connectors: {total_connectors}'])]),
                dhtml.Tr(children=[
                    dhtml.Td(children=[
                        dhtml.Table(className='table-info-secondary', children=[
                            dhtml.Tr(children=[
                                dhtml.Td(children=['Input:']),
                                dhtml.Td(children=[f'{number_inputs}'])]),
                            dhtml.Tr(children=[
                                dhtml.Td(children=['Output:']),
                                dhtml.Td(children=[f'{number_outputs}'])])
                        ])])])
            ])
        ])
