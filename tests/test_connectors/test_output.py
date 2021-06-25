"""Tests the functionality of ``Output`` connector objects."""

from unittest import TestCase

from egon import exceptions
from egon.connectors import Input, Output
from egon.exceptions import MissingConnectionError


class DataPut(TestCase):
    """Test data routing by ``Output`` instances"""

    def test_stores_value_in_queue(self) -> None:
        """Test the ``put`` method puts data into the underlying connected queue"""

        # Create a node with an output connector
        output = Output()
        input = Input()
        output.connect(input)

        test_val = 'test_val'
        output.put(test_val)
        self.assertEqual(input._queue.get(), test_val)

    def test_error_if_unconnected(self) -> None:
        """Test ``put`` raises an error if the output is not connected"""

        with self.assertRaises(MissingConnectionError):
            Output().put(5)

    @staticmethod
    def test_error_override() -> None:
        """Test the optional suppression of errors for unconnected outputs"""

        Output().put(5, raise_missing_connection=False)


class InstanceConnect(TestCase):
    """Test the connection of generic connector objects to other"""

    def setUp(self) -> None:

        self.input_connector = Input()
        self.output_connector = Output()

    def test_error_on_connection_to_same_type(self) -> None:
        """Test an error is raised when connecting two outputs together"""

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
        """Test both connectors are no longer listed as partners"""

        self.assertTrue(self.input.is_connected())
        self.assertTrue(self.output.is_connected())

        self.output.disconnect(self.input)
        self.assertNotIn(self.output, self.input.partners)
        self.assertFalse(self.input.is_connected())
        self.assertFalse(self.output.is_connected())

    def test_error_if_not_connected(self) -> None:
        """Test an error is raised when disconnecting a connector that is not connected"""

        with self.assertRaises(MissingConnectionError):
            Output().disconnect(Input())
