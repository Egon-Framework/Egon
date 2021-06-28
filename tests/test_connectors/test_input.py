"""Tests for ``Input`` connector objects."""

import time
from unittest import TestCase

from egon.connectors import Input, KillSignal
from egon.exceptions import MissingConnectionError
from egon.mock import MockTarget


class InputGet(TestCase):
    """Test data retrieval from ``Input`` instances"""

    def setUp(self) -> None:
        self.input_connector = Input()

    def test_error_on_non_positive_refresh(self) -> None:
        """Test a ValueError is raised when ``refresh_interval`` is not a positive number"""

        with self.assertRaises(ValueError):
            self.input_connector.get(timeout=15, refresh_interval=0)

        with self.assertRaises(ValueError):
            self.input_connector.get(timeout=15, refresh_interval=-1)

    def test_returns_queue_value(self) -> None:
        """Test the ``get`` method retrieves data from the underlying queue"""

        test_val = 'test_val'
        self.input_connector._queue.put(test_val)

        time.sleep(1)
        self.assertEqual(test_val, self.input_connector.get(timeout=1000))

    def test_timeout_raises_timeout_error(self) -> None:
        """Test a ``TimeoutError`` is raise on timeout"""

        with self.assertRaises(TimeoutError):
            self.input_connector.get(timeout=1)

    def test_kill_signal_on_finished_parent_node(self) -> None:
        """Test a kill signal is returned if the parent node is finished"""

        target = MockTarget()
        self.assertFalse(target.is_expecting_data())
        self.assertIs(target.input.get(timeout=15), KillSignal)


class InputIterGet(TestCase):
    """Test iteration behavior of the ``iter_get`` method"""

    def setUp(self) -> None:
        """Create an input connector that is assigned to a parent node

        The input connector must be assigned to a parent node, otherwise
        ``iter_get`` raises an error.
        """

        self.input_connector = MockTarget().input

    def test_raises_stop_iteration_on_kill_signal(self) -> None:
        """Test the iterator exits once it reaches a KillSignal object"""

        self.input_connector._queue.put(KillSignal)
        with self.assertRaises(StopIteration):
            next(self.input_connector.iter_get())

    def test_raises_missing_connection_with_no_parent(self) -> None:
        """Test the iterator exits if input has no paren"""

        with self.assertRaises(MissingConnectionError):
            next(Input().iter_get())

    def test_returns_queue_value(self) -> None:
        """Test the ``get`` method retrieves data from the underlying queue"""

        test_val = 'test_val'
        self.input_connector._queue.put(test_val)
        time.sleep(1)  # Give queue time to update

        self.assertEqual(next(self.input_connector.iter_get()), test_val)


class MaxSize(TestCase):
    """Tests the setting/getting of the maximum size for the underlying queue"""

    def setUp(self) -> None:
        self.connector = Input(maxsize=10)

    def test_queue_matches_input(self) -> None:
        """Test the max size of the underlying queue matches the max size of the Input"""

        self.assertEqual(self.connector._queue._maxsize, self.connector.maxsize)

    def test_set_at_init(self) -> None:
        """Test the max queue size is set at __init__"""

        self.assertEqual(10, self.connector.maxsize)

    def test_changed_via_setter(self) -> None:
        """Test the size of the underlying queue is changed when setting the ``maxsize`` attribute"""

        self.connector.maxsize = 5
        self.assertEqual(5, self.connector.maxsize)

    def test_error_on_nonempty_queue(self) -> None:
        """Test a ``RuntimeError`` is raised when changing the size of a nonempty connector"""

        self.connector._queue.put(1)
        time.sleep(1)  # Let the queue update

        with self.assertRaises(RuntimeError):
            self.connector.maxsize += 1


class QueueProperties(TestCase):
    """Test  test the exposure of queue properties by the overlying ``Connector`` class"""

    def setUp(self) -> None:
        self.connector = Input(maxsize=1)

    def test_size_matches_queue_size(self) -> None:
        """Test the ``size`` method returns the size of the queue`"""

        self.assertEqual(self.connector.size(), 0)
        self.connector._queue.put(1)
        self.assertEqual(self.connector.size(), 1)

    def test_full_state(self) -> None:
        """Test the ``full`` method returns the state of the queue"""

        self.assertFalse(self.connector.is_full())
        self.connector._queue.put(1)
        self.assertTrue(self.connector.is_full())

    def test_empty_state(self) -> None:
        """Test the ``empty`` method returns the state of the queue"""

        self.assertTrue(self.connector.is_empty())
        self.connector._queue.put(1)

        # The value of Queue.is_empty() updates asynchronously
        time.sleep(1)

        self.assertFalse(self.connector.is_empty())
