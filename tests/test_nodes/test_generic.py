"""Tests for the class based construction of pipeline nodes."""

from functools import partial
from unittest import TestCase

from egon import mock


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
        self.internal_node = mock.MockNode()
        self.leaf = mock.MockTarget()

        self.root.output.connect(self.internal_node.input)
        self.internal_node.output.connect(self.leaf.input)

    def test_upstream_nodes(self) -> None:
        """Test the inline node resolves the correct parent node"""

        self.assertEqual(self.root, self.internal_node.upstream_nodes()[0])

    def test_downstream_nodes(self) -> None:
        """Test the inline node resolves the correct child node"""

        self.assertEqual(self.leaf, self.internal_node.downstream_nodes()[0])


class ExpectingData(TestCase):
    """Tests for the ``is_expecting_data`` function

    The ``is_expecting_data`` function combines two booleans.
    This class evaluates all four squares of the corresponding truth table
    """

    def setUp(self) -> None:
        """Create a tree of ``MockNode`` instances"""

        # Fork zero processes so we can control the node finished state as the state of the daemon process
        self.root = mock.MockSource(num_processes=0)
        self.node = mock.MockNode(num_processes=0)
        self.root.output.connect(self.node.input)

    def test_false_for_empty_queue_and_finished_parent(self) -> None:
        """Test the return is False for a EMPTY queue and a FINISHED PARENT node"""

        self.root._process_finished = True
        self.assertFalse(self.node.is_expecting_data)

    def test_true_if_input_queue_has_data(self) -> None:
        """Test the return is True for a NOT EMPTY queue and a FINISHED PARENT node"""

        self.root._process_finished = True
        self.node.input._queue.put(5)
        self.assertTrue(self.node.is_expecting_data)

    def test_true_if_parent_is_running(self) -> None:
        """Test the return is True for a EMPTY queue and a NOT FINISHED PARENT node"""

        self.root._process_finished = False
        self.assertTrue(self.node.is_expecting_data)

    def test_true_if_input_queue_has_data_and_parent_is_running(self) -> None:
        """Test the return is True for a NOT EMPTY queue and a NOT FINISHED PARENT node"""

        self.root._process_finished = False
        self.node.input._queue.put(5)
        self.assertTrue(self.node.is_expecting_data)
