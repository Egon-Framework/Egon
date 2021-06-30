"""The Pipeline module defines the ``Pipeline`` class which is responsible
for representing collections of interconnected analysis steps (``Node``
objects) as a  single, coherent analysis pipeline. ``Pipeline`` instances
are also responsible for starting/stopping forked processes and validating
that nodes are properly interconnected.
"""

from __future__ import annotations

import os
import warnings
from asyncio.subprocess import Process
from copy import copy
from inspect import getmembers
from itertools import chain
from typing import List, Tuple

from . import connectors as conn
from . import nodes
from .visualize import Visualizer


class Pipeline:
    """Manages a collection of nodes as a single analysis pipeline"""

    def __init__(self) -> None:

        # Store the nodes and connectors used to build the pipeline
        # so they can be exposed by public accessors
        self._inputs: List[conn.Input] = []
        self._outputs: List[conn.Output] = []
        self._sources: List[nodes.Source] = []
        self._inlines: List[nodes.Node] = []
        self._targets: List[nodes.Target] = []

        for attr_name, *_ in getmembers(self, lambda a: isinstance(a, nodes.AbstractNode)):
            node = getattr(self, attr_name)
            if isinstance(node, nodes.Node):
                self._inlines.append(node)

            elif isinstance(node, nodes.Source):
                self._sources.append(node)

            else:  # Assume all other nodes are inlines
                self._targets.append(node)

            inputs, outputs = node.connectors
            self._inputs.extend(inputs)
            self._outputs.extend(outputs)

    def validate(self) -> None:
        """Set up the pipeline and check for any invalid node states"""

        for node in chain(*self.nodes):
            node.validate()

    def _get_processes(self) -> List[Process]:
        """Return a list of processes forked by pipeline nodes"""

        # Collect all of the processes assigned to each node
        processes = []
        for node in chain(*self.nodes):
            processes.extend(node._pool._processes)

        return processes

    @property
    def nodes(self) -> Tuple[Tuple[nodes.Source], Tuple[nodes.Node], Tuple[nodes.Target]]:
        """Return a list of all nodes in the pipeline

        Nodes are returned in an arbitrary order

        Returns:
            A list of nodes used to build the pipeline
        """

        return tuple(self._sources), tuple(self._inlines), tuple(self._targets)

    @property
    def connectors(self) -> Tuple[List[conn.Input], List[conn.Output]]:
        """Return the input and output connectors used by the pipeline

        Returns:
            A tuple with a list of input connectors and a list of output connectors
        """

        return copy(self._inputs), copy(self._outputs)

    @property
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

        for node in chain(*self.nodes):
            node._pool.join()

    def run_async(self) -> None:
        """Start all processes asynchronously"""

        for node in chain(*self.nodes):
            node._pool.start()

    def visualize(
            self,
            host: str = os.getenv("EGON_HOST", "127.0.0.1"),
            port: int = os.getenv("EGON_PORT", "8050"),
            quiet: bool = False
    ) -> None:
        """Launch a server instance for monitoring the pipeline in real time

        This is a blocking call intended to be run in the main application
        process.

        Args:
            host: Host IP used to serve the application
            port: Port used to serve the application
            quiet: Suppress any status messages or warnings
        """

        from waitress import serve

        if not quiet:
            print(f'Launching server at http://{host}:{port}')

        # we increase the number of threads from 4 (the default) to 8 so the
        # server can more efficiently handle all of the application callbacks
        with warnings.catch_warnings():
            if quiet:
                warnings.simplefilter('ignore')

            serve(Visualizer(self).server, host=host, port=int(port), threads=8, _quiet=quiet)
