"""Tests for the class based construction of pipeline nodes."""

from functools import partial
from time import sleep
from unittest import TestCase

from egon import mock
from egon.exceptions import MissingConnectionError
from egon.mock import MockSource


class Execution(TestCase):
    """Test the execution of tasks assigned to a Node instance"""

    def setUp(self) -> None:
        """Create a testing node that tracks the execution method of it's methods"""

        self.node = mock.MockNode()

        # Track the call order of node functions
        self.call_list = []
        self.node.setup = partial(self.call_list.append, 'setup')
        self.node.action = partial(self.call_list.append, 'action')
        self.node.teardown = partial(self.call_list.append, 'teardown')

    def test_call_order(self) -> None:
        """Test that setup and teardown actions are called in the correct order"""

        self.node.execute()
        self.assertListEqual(self.call_list, ['setup', 'action', 'teardown'])


class TreeNavigation(TestCase):
    """Test ``Node`` instances are aware of their neighbors"""

    def setUp(self) -> None:
        """Create a tree of ``MockNode`` instances"""

        self.root = mock.MockSource()
        self.inline = mock.MockNode()
        self.target = mock.MockTarget()

        self.root.output.connect(self.inline.input)
        self.inline.output.connect(self.target.input)

    def test_upstream_nodes(self) -> None:
        """Test the inline node resolves the correct parent node"""

        self.assertEqual(self.root, self.inline.upstream_nodes[0])
        self.assertEqual(self.inline, self.target.upstream_nodes[0])

    def test_downstream_nodes(self) -> None:
        """Test the inline node resolves the correct child node"""

        self.assertEqual(self.inline, self.root.downstream_nodes[0])
        self.assertEqual(self.target, self.inline.downstream_nodes[0])


class ExpectingData(TestCase):
    """Tests for the ``is_expecting_data`` function

    The ``is_expecting_data`` function combines two booleans.
    This class evaluates all four squares of the corresponding truth table
    """

    def setUp(self) -> None:
        """Create a tree of ``MockNode`` instances"""

        self.root = mock.MockSource()
        self.node = mock.MockNode()
        self.root.output.connect(self.node.input)

    def test_false_for_empty_queue_and_finished_parent(self) -> None:
        """Test the return is False for a EMPTY queue and a FINISHED PARENT node"""

        self.root.execute()
        self.assertFalse(self.node.is_expecting_data())

    def test_true_if_input_queue_has_data(self) -> None:
        """Test the return is True for a NOT EMPTY queue and a FINISHED PARENT node"""

        self.root.execute()
        self.node.input._queue.put(5)
        sleep(1)  # Give the queue an opportunity to update

        self.assertTrue(self.node.is_expecting_data())

    def test_true_if_parent_is_running(self) -> None:
        """Test the return is True for a EMPTY queue and a NOT FINISHED PARENT node"""

        self.assertTrue(self.node.is_expecting_data())

    def test_true_if_input_queue_has_data_and_parent_is_running(self) -> None:
        """Test the return is True for a NOT EMPTY queue and a NOT FINISHED PARENT node"""

        self.node.input._queue.put(5)
        self.assertTrue(self.node.is_expecting_data())


class ConnectorValidation(TestCase):
    """Test the validation of underlying connector objects"""

    def test_missing_connection(self) -> None:
        """Test a ``MissingConnectionError`` for an unconnected connector"""

        with self.assertRaises(MissingConnectionError):
            MockSource().validate()
