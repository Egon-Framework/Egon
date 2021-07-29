"""The ``mock`` module defines prebuilt pipeline nodes for developing
unittests. Instead of accomplishing a user defined action, mock nodes sleep
for a pre-defined number of seconds.
"""

from abc import ABC

from egon import nodes
from egon.connectors import Input, Output
from egon.nodes import AbstractNode


class Mock(AbstractNode, ABC):
    """Base class for mock testing nodes"""

    def __init__(self) -> None:
        self._is_running = False
        super(Mock, self).__init__()

    def set_running_state(self, state: bool) -> None:
        """Set the return value of the ``is_running`` method

        Args:
            state: The returned running state
        """

        self._is_running = state

    def is_running(self) -> bool:
        """Return if any node processes are still processing data

        This is a mock value that can be changed using the
        ``set_running_state`` function. Mock node values do not create
        spawned processes.
        """

        return self._is_running

    def execute(self) -> None:
        """Execute the mock pipeline node"""

        super(Mock, self).execute()


class MockSource(Mock, nodes.Source):
    """A mock ``Source`` node for use in testing"""

    def __init__(self, load_data: list = None) -> None:
        """A Mock Source node with a single output connector

        On execution, data from the ``load_data`` argument is loaded into the
        ``output`` connector.

        Args:
            load_data: Data to load into the output connector
        """

        self.output = Output()
        self.load_data = load_data or []
        super(MockSource, self).__init__()

    def action(self) -> None:
        """Placeholder function to satisfy requirements of abstract parent"""

        for x in self.load_data:
            self.output.put(x)


class MockTarget(Mock, nodes.Target):
    """A mock ``Target`` node for use in testing"""

    def __init__(self) -> None:
        """A Mock ``Target`` node with a single input connector

        On execution, data from the ``input`` connector is loaded into the
        ``accumulated_data`` attribute.
        """

        self.input = Input()
        self.accumulated_data = []
        super(MockTarget, self).__init__()

    def action(self) -> None:
        """Placeholder function to satisfy requirements of abstract parent"""

        for x in self.input.iter_get():
            self.accumulated_data.append(x)


class MockNode(Mock, nodes.Node):
    """A mock ``Node`` object for use in testing"""

    def __init__(self) -> None:
        """A Mock ``Target`` node with an input and output connector

        On execution, data from the ``input`` connector is loaded into the
        ``output`` connector.
        """

        self.output = Output()
        self.input = Input()
        super(MockNode, self).__init__()

    def action(self) -> None:  # pragma: no cover
        """Placeholder function to satisfy requirements of abstract parent"""

        for x in self.input.iter_get():
            self.output.put(x)
