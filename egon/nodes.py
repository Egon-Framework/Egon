"""``Node`` objects represent individual analysis steps in a data analysis
pipeline.
"""

from __future__ import annotations

import abc
from typing import Tuple

from . import connectors


class Node(abc.ABC):
    """Abstract base class for constructing analysis nodes"""

    def __init__(self, name: str = None, num_processes: int = 1) -> None:
        """Instantiate a new pipeline node

        Args:
            name: Set a descriptive name for the connector object
            num_processes: The number of processes to allocate to the node instance
        """

    @property
    def num_processes(self) -> int:
        """The number of processes assigned to the analysis node"""

    @num_processes.setter
    def num_processes(self, val) -> None:
        ...

    def input_connectors(self) -> Tuple[connectors.Input, ...]:
        """Return a collection of input connectors attached to this node"""

    def output_connectors(self) -> Tuple[connectors.Input, ...]:
        """Return a collection of output connectors attached to this node"""

    @property
    def upstream_nodes(self) -> Tuple[Node]:
        """Return a list of upstream nodes connected to the current node"""

    @property
    def downstream_nodes(self) -> Tuple[Node]:
        """Return a list of downstream nodes connected to the current node"""

    def validate(self) -> None:
        """Validate the current node has no obvious connection issues

        Raises:
            NodeValidationError: If the node does not validate properly
        """

    @classmethod
    def class_setup(cls) -> None:
        """Setup tasks for configuring the parent class

        This method is called once to set up the parent class before launching
        any child processes.

        For the corresponding teardown logic, see the ``class_teardown`` method.
        """

    def setup(self) -> None:
        """Setup tasks for configuring individual child processes

        This method is called once by every node instance within each
        child process.

        For the corresponding teardown logic, see the ``teardown`` method.
        """

    @abc.abstractmethod
    def action(self) -> None:
        """The primary analysis task performed by this node"""

    def teardown(self) -> None:
        """teardown tasks for cleaning up after individual child processes

        This method is called once before exiting each child process.

        For the corresponding setup logic, see the ``setup`` method.
        """

    @classmethod
    def class_teardown(cls) -> None:
        """teardown tasks for cleaning up after the parent class

        This method is called once after all child processes have been terminated.

        For the corresponding setup logic, see the ``class_setup`` method.
        """

    def execute(self):
        """Execute the pipeline node, including all setup and teardown tasks"""

    def is_finished(self) -> bool:
        """Return whether all node processes have finished processing data

        The returned value defaults to ``True`` when the number of child
        processes attached to the node is zero.
        """

    def is_expecting_data(self) -> bool:
        """Return whether the node is still expecting data from upstream nodes

        This method checks whether any connected, upstream nodes are still
        running and whether there is still data pending in any input connectors.
        """

    def __str__(self) -> str:
        """Return a string representation of the parent instance"""