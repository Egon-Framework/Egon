"""Tests for the ``Pipeline`` class"""

from time import sleep
from unittest import TestCase

from egon.exceptions import MissingConnectionError, OrphanedNodeError
from egon.mock import MockPipeline, MockSource
from egon.nodes import Node
from egon.pipeline import Pipeline


class StartStopCommands(TestCase):
    """Test processes are launched and terminated on command"""

    def runTest(self) -> None:
        """Launch and then kill the process manager"""

        pipeline = MockPipeline()
        self.assertFalse(pipeline.any_alive())

        pipeline.run_async()
        self.assertTrue(pipeline.all_alive())

        pipeline.kill()
        sleep(1)  # Give the process time to exit
        self.assertFalse(pipeline.any_alive())


class ProcessDiscovery(TestCase):
    """Test the pipeline is aware of all processes forked by it's nodes"""

    def test_collected_processes_match_nodes(self) -> None:
        """Test ``_get_processes`` returns forked processes from all pipeline nodes"""

        pipeline = MockPipeline()
        expected_processes = []
        expected_processes.extend(pipeline.source._processes)
        expected_processes.extend(pipeline.target._processes)
        self.assertCountEqual(expected_processes, pipeline._get_processes())

    def test_process_count(self) -> None:
        """Test the pipelines process count matches the sum of processes allocated to each node"""

        pipeline = MockPipeline()
        expected_count = pipeline.source.num_processes + pipeline.target.num_processes
        self.assertEqual(expected_count, pipeline.num_processes())


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


class NodeDiscovery(TestCase):
    """Test the pipeline is aware of all of it's nodes"""

    def runTest(self) -> None:
        pipeline = MockPipeline()
        sources, inlines, targets = pipeline.nodes
        self.assertCountEqual([pipeline.source], sources)
        self.assertCountEqual([], inlines)
        self.assertCountEqual([pipeline.target], targets)
