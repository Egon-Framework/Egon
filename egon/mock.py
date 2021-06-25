"""The ``mock`` module defines prebuilt pipeline nodes for developing
unittests. Instead of accomplishing a user defined action, mock nodes sleep
for a pre-defined number of seconds.
"""

from egon import nodes
from egon.nodes import MPool
from egon.connectors import Input, Output


class Mock:
    """Base class for mock testing nodes"""

    def run_mock(self) -> None:
        self._pool: MPool
        self._pool.start()
        self._pool.join()


class MockSource(Mock, nodes.Source):
    """A ``Source`` subclass that implements placeholder functions for abstract methods"""

    def __init__(self, load_data: list = None) -> None:
        self.output = Output()
        self.load_data = load_data or []
        super(MockSource, self).__init__(num_processes=1)

    def action(self) -> None:
        """Placeholder function to satisfy requirements of abstract parent"""

        for x in self.load_data:
            self.output.put(x)


class MockTarget(Mock, nodes.Target):
    """A ``Target`` subclass that implements placeholder functions for abstract methods"""

    def __init__(self) -> None:
        self.input = Input()
        self.accumulated_data = []
        super(MockTarget, self).__init__(num_processes=1)

    def action(self) -> None:
        """Placeholder function to satisfy requirements of abstract parent"""

        for x in self.input.iter_get():
            self.accumulated_data.append(x)


class MockNode(Mock, nodes.Node):
    """A ``Node`` subclass that implements placeholder functions for abstract methods"""

    def __init__(self) -> None:
        self.output = Output()
        self.input = Input()
        super(MockNode, self).__init__(num_processes=1)

    def action(self) -> None:  # pragma: no cover
        """Placeholder function to satisfy requirements of abstract parent"""

        for x in self.input.iter_get():
            self.output.put(x)
