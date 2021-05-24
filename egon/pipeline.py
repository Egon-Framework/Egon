"""The Pipeline module defines the ``Pipeline`` class which is responsible
for representing collections of interconnected analysis steps (``Node``
objects) as a  single, coherent analysis pipeline. ``Pipeline`` instances
are also responsible for starting/stopping forked processes and validating
that nodes are properly interconnected.
"""

from __future__ import annotations

from asyncio.subprocess import Process
from copy import copy
from inspect import getmembers
from typing import List, Tuple

from .connectors import Input, Output
from .nodes import AbstractNode


class Pipeline:
    """Manages a collection of nodes as a single analysis pipeline"""

    def __init__(self):
        self._nodes = [getattr(self, a[0]) for a in getmembers(self, lambda a: isinstance(a, AbstractNode))]

        self._inputs, self._outputs = [], []
        for node in self.node_list:
            for connector in node.get_connectors():
                if isinstance(connector, Input):
                    self._inputs.append(connector)

                if isinstance(connector, Output):
                    self._outputs.append(connector)

    def validate(self) -> None:
        """Set up the pipeline and check for any invalid node states"""

        # Make sure the nodes are in a runnable condition before we start spawning processes
        for node in self.node_list:
            node.validate()

    def _get_processes(self) -> List[Process]:
        """Return a list of processes forked by pipeline nodes"""

        # Collect all of the processes assigned to each node
        processes = []
        for node in self.node_list:
            processes.extend(node._processes)

        return processes

    @property
    def node_list(self) -> List[AbstractNode]:
        """Return a list of all nodes in the pipeline

        Nodes are returned in an arbitrary order

        Returns:
            A list of nodes used to build the pipeline
        """

        return copy(self._nodes)

    @property
    def connectors(self) -> Tuple[List[Input], List[Output]]:
        """Return the input and output connectors used by the pipeline

        Returns:
            A tuple with a list of input connectors and a list of output connectors
        """

        return copy(self._inputs), copy(self._outputs)

    def num_processes(self) -> int:
        """The number of processes forked by to the pipeline"""

        return len(self._get_processes())

    def kill(self) -> None:
        """Kill all running pipeline processes without trying to exit gracefully"""

        for p in self._get_processes():
            p.terminate()

    def run(self) -> None:
        """Start all pipeline processes and block execution until all processes exit"""

        self.run_async()
        self.wait_for_exit()

    def wait_for_exit(self) -> None:
        """Wait for the pipeline to finish running before continuing execution"""

        for p in self._get_processes():
            p.join()

    def run_async(self) -> None:
        """Start all processes asynchronously"""

        for p in self._get_processes():
            p.start()
