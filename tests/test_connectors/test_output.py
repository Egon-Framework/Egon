"""Tests the functionality of ``Output`` connector objects."""

from time import sleep
from unittest import TestCase

from egon import exceptions
from egon.connectors import Input, Output
from egon.exceptions import MissingConnectionError
from egon.mock import MockSource, MockTarget


class DataPut(TestCase):
    """Test data storage in ``Output`` instances"""

    def setUp(self) -> None:
        """Define an ``Output`` instance"""

        # Create a node with an output connector
        self.source = MockSource()
        self.target = MockTarget()
        self.source.output.connect(self.target.input)

    def test_stores_value_in_queue(self) -> None:
        """Test the ``put`` method retrieves data from the underlying queue"""

        test_val = 'test_val'
        self.source.output.put(test_val)
        self.assertEqual(self.target.input._queue.get(), test_val)

    def test_error_if_unconnected(self) -> None:
        with self.assertRaises(MissingConnectionError):
            Output().put(5)

    @staticmethod
    def test_error_override() -> None:
        Output().put(5, raise_missing_connection=False)

    def test_multiple_connection_support(self):
        """Test output connectors support sending data to multiple input connectors"""

        # Create one node to output data and two to accept it
        test_data = [1, 2, 3]
        source = MockSource(test_data)
        target_a = MockTarget()
        target_b = MockTarget()

        # Connect two outputs to the same input
        source.output.connect(target_a.input)
        source.output.connect(target_b.input)
        source.execute()
        sleep(1)  # Give the queue a chance to update

        # Both inputs should have received the same data from the output
        target_a.execute()
        self.assertListEqual(test_data, target_a.accumulated_data)

        target_b.execute()
        self.assertListEqual(test_data, target_b.accumulated_data)


class InstanceConnections(TestCase):
    """Test the connection of generic connector objects to other"""

    def setUp(self) -> None:
        """Define a generic ``Connector`` instance"""

        self.input_connector = Input()
        self.output_connector = Output()

    def test_error_on_connection_to_same_type(self) -> None:
        """An error is raised when connecting two inputs together"""

        with self.assertRaises(ValueError):
            self.output_connector.connect(Output())

    def test_overwrite_error_on_connection_overwrite(self) -> None:
        """Test an error is raised when trying to overwrite an existing connection"""

        input = Input()
        self.output_connector.connect(input)
        with self.assertRaises(exceptions.OverwriteConnectionError):
            self.output_connector.connect(input)


class InstanceDisconnect(TestCase):
    """Test the disconnection of two connectors"""

    def setUp(self) -> None:
        self.input = Input()
        self.output = Output()
        self.output.connect(self.input)

    def test_both_connectors_are_disconnected(self) -> None:
        """Test calling disconnect from one connector results in both connectors being disconnected"""

        self.output.disconnect(self.input)
        self.assertNotIn(self.output, self.input.get_partners())

    def test_error_if_not_connected(self):
        """Test an error is raised when disconnecting a connector that is not connected"""

        with self.assertRaises(MissingConnectionError):
            Output().disconnect(Input())
