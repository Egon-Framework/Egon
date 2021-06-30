"""Tests for the connection of multiple inputs and outputs together"""

from time import sleep
from unittest import TestCase

from egon.connectors import Input, Output
from egon.mock import MockSource, MockTarget


class MultiplePartnerMapping(TestCase):
    """Test connectors with an established connection correctly map to neighboring connectors/nodes"""

    def setUp(self) -> None:
        """Connect two outputs to a single input"""

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


class MultiplePartnerDataRouting(TestCase):
    """Test output connectors support sending data to multiple input connectors"""

    def runTest(self) -> None:
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
