from unittest import TestCase

from egon.connectors import Input, Output


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
        self.assertCountEqual(output_connectors, self.input.partners)

    def test_input_maps_to_partners(self) -> None:
        """Test connectors map to the correct partner connector"""

        input_connectors = [self.input]
        self.assertCountEqual(input_connectors, self.output1.partners)
        self.assertCountEqual(input_connectors, self.output2.partners)

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


class ConnectionState(TestCase):
    """Test that connectors are aware of their connection state"""

    def setUp(self) -> None:
        self.input = Input()
        self.output = Output()

    def test_state_change_when_connected(self) -> None:
        """Test that the connection state changes once to connectors are assigned together"""

        self.output.connect(self.input)
        self.assertTrue(self.input.is_connected())
        self.assertTrue(self.output.is_connected())

    def test_state_resets_on_disconnect(self) -> None:
        """Test the connection state resets to False once connections are separated"""

        self.output.connect(self.input)
        self.output.disconnect(self.input)
        self.assertFalse(self.input.is_connected())
        self.assertFalse(self.output.is_connected())
