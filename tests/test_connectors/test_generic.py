"""Tests that connector objects are able to connect together properly"""

from unittest import TestCase

from egon.connectors import Input, Output
from egon.mock import MockSource


class ParentMapping(TestCase):
    """Test connector objects are aware of their parents"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_node = MockSource()

    def test_maps_to_parent(self):
        """Test the connector assigned to a node returns that node as it's parent"""

        self.assertEqual(self.test_node, self.test_node.output.parent_node)


class PartnerMapping(TestCase):
    """Test connectors with an established connection correctly map to neighboring connectors/nodes"""

    def setUp(self) -> None:
        """Create two connected pipeline elements"""

        self.input = Input()
        self.output1 = Output()
        self.output2 = Output()

        self.output1.connect(self.input)
        self.output2.connect(self.input)

    def test_output_maps_to_partners(self) -> None:
        """Test connectors map to the correct partner connector"""

        output_connectors = [self.output1, self.output2]
        self.assertCountEqual(output_connectors, self.input.get_partners())

    def test_input_maps_to_partners(self) -> None:
        """Test connectors map to the correct partner connector"""

        input_connectors = [self.input]
        self.assertCountEqual(input_connectors, self.output1.get_partners())
        self.assertCountEqual(input_connectors, self.output2.get_partners())


class ConnectionState(TestCase):
    """Test that connectors are aware of their connection state"""

    def setUp(self) -> None:
        self.input = Input()
        self.output = Output()

    def test_default_connection_false(self):
        """Test connectors are disconnected by default"""

        self.assertFalse(self.input.is_connected)
        self.assertFalse(self.output.is_connected)

    def test_state_change_when_connected(self):
        """Test that the connection state changes once to connectors are assigned together"""

        self.output.connect(self.input)
        self.assertTrue(self.input.is_connected)
        self.assertTrue(self.output.is_connected)

    def test_state_resets_on_disconnect(self):
        """Test the connection state resets to False once connections are separated"""

        self.output.connect(self.input)
        self.output.disconnect(self.input)
        self.assertFalse(self.input.is_connected)
        self.assertFalse(self.output.is_connected)
