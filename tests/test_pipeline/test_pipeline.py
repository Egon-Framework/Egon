"""Tests for the ``Pipeline`` class"""

from unittest import TestCase

from egon.exceptions import MissingConnectionError, OrphanedNodeError
from egon.mock import MockNode, MockSource, MockTarget
from egon.nodes import Node
from egon.pipeline import Pipeline


class SimplePipeline(Pipeline):
    """Basic pipeline for testing the parent pipeline class"""

    def __init__(self) -> None:
        self.source = MockSource([1, 2, 3])
        self.inline = MockNode()
        self.target = MockTarget()

        self.source.output.connect(self.inline.input)
        self.inline.output.connect(self.target.input)
        super(SimplePipeline, self).__init__()


class ProcessDiscovery(TestCase):
    """Test the pipeline is aware of all processes forked by it's nodes"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pipeline = SimplePipeline()
        cls.expected_processes = []
        cls.expected_processes.extend(cls.pipeline.source._pool._processes)
        cls.expected_processes.extend(cls.pipeline.inline._pool._processes)
        cls.expected_processes.extend(cls.pipeline.target._pool._processes)

    def test_collected_processes_match_nodes(self) -> None:
        """Test ``_get_processes`` returns forked processes from all pipeline nodes"""

        self.assertCountEqual(self.expected_processes, self.pipeline._get_processes())

    def test_process_count(self) -> None:
        """Test the pipelines process count matches the sum of processes allocated to each node"""

        self.assertEqual(len(self.expected_processes), self.pipeline.num_processes)


class NodeDiscovery(TestCase):
    """Test the pipeline is aware of all it's nodes"""

    def runTest(self) -> None:
        """Instantiate a test pipeline and ask it for it's available nodes"""

        pipeline = SimplePipeline()
        sources, inlines, targets = pipeline.nodes

        self.assertEqual((pipeline.source,), sources)
        self.assertEqual((pipeline.inline,), inlines)
        self.assertEqual((pipeline.target,), targets)


class ConnectorDiscovery(TestCase):
    """Test the pipeline is aware of all it's connector objects"""

    def runTest(self) -> None:
        """Instantiate a test pipeline and ask it for it's available nodes"""

        pipeline = SimplePipeline()
        expected_inputs = []
        expected_inputs.extend(pipeline.source.connectors[0])
        expected_inputs.extend(pipeline.inline.connectors[0])
        expected_inputs.extend(pipeline.target.connectors[0])

        expected_outputs = []
        expected_outputs.extend(pipeline.source.connectors[1])
        expected_outputs.extend(pipeline.inline.connectors[1])
        expected_outputs.extend(pipeline.target.connectors[1])

        self.assertCountEqual(expected_inputs, pipeline.connectors[0])
        self.assertCountEqual(expected_outputs, pipeline.connectors[1])


class PipelineValidation(TestCase):
    """Test appropriate errors are raised for an invalid pipeline."""

    def test_orphaned_node(self) -> None:
        """Test a ``OrphanedNodeError`` for an unreachable node"""

        class OrphanedNode(Node):
            def action(self) -> None:
                pass

        class Pipe(Pipeline):
            def __init__(self) -> None:
                self.node = OrphanedNode()
                super().__init__()

        with self.assertRaises(OrphanedNodeError):
            Pipe().validate()

    def test_missing_connection(self) -> None:
        """Test a ``MissingConnectionError`` for an unconnected connector"""

        class Pipe(Pipeline):
            def __init__(self) -> None:
                self.root = MockSource()
                super().__init__()

        with self.assertRaises(MissingConnectionError):
            Pipe().validate()
