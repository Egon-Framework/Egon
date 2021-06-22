import multiprocessing as mp
from time import sleep
from typing import Any, Collection, Iterable, Optional


class KillSignal:
    """Used to indicate that a process should exit"""


class ObjectCollection:
    """Collection of objects with O(1) add and remove"""

    def __init__(self, data: Optional[Collection] = None) -> None:
        """A mutable collection of arbitrary objects

        Args:
            data: Populate the collection instance with the given data
        """

        # Map object hash values to their index in a list
        self._object_list = list(set(data)) if data else []
        self._index_map = {o: i for i, o in enumerate(self._object_list)}

    def add(self, x: Any) -> None:
        """Add a hashable object to the collection

        Args:
            x: The object to add
        """

        # Exit if ``x`` is already in the collection
        if x in self._index_map:
            return

        # Add ``x`` to the end of the collection
        self._index_map[x] = len(self._object_list)
        self._object_list.append(x)

    def remove(self, x: Any) -> None:
        """Remove an object from the collection

        Args:
            x: The object to remove
        """

        index = self._index_map[x]

        # Swap element with last element so that removal from the list can be done in O(1) time
        size = len(self._object_list)
        last = self._object_list[size - 1]
        self._object_list[index], self._object_list[size - 1] = self._object_list[size - 1], self._object_list[index]

        # Update hash table for new index of last element
        self._index_map[last] = index

        del self._index_map[x]
        del self._object_list[-1]

    def __iter__(self) -> Iterable:
        return iter(self._object_list)

    def __contains__(self, item: Any) -> bool:
        return item in self._object_list

    def __len__(self) -> int:
        return len(self._object_list)

    def __repr__(self) -> str:  # pragma: no cover
        return f'<Container({self._object_list})>'


class MPool:
    """A pool of processes assigned to a single target function"""

    def __init__(self, num_processes: int, target: callable) -> None:
        """Create a collection of processes assigned to execute a given callable

        Args:
            num_processes: The number of processes to spawn
            target: The function each process should execute
        """

        self._processes = []
        self._current_process_state = False

        self._target = target
        self.num_processes = num_processes

    def _call_target(self) -> None:  # pragma: nocover, Called from forked process
        """Wrapper for the user provided target function"""

        self._target()
        self._process_finished = True

    @property
    def num_processes(self) -> int:
        """The number of processes assigned to the current node"""

        return len(self._processes)

    @num_processes.setter
    def num_processes(self, num_processes: int) -> None:
        """The number of processes assigned to the current node"""

        if num_processes <= 0:
            raise ValueError(f'Cannot instantiate less than 1 forked processes (got {num_processes}).')

        if any(p.is_alive() for p in self._processes):
            raise RuntimeError('Cannot change number of processes while node is running.')

        # Note that we use the memory address of the processes and not the
        # ``pid`` attribute. ``pid`` is only set after the process is started.
        self._processes = [mp.Process(target=self._call_target) for _ in range(num_processes)]
        self._states = mp.Manager().dict({id(p): False for p in self._processes})

    @property
    def _process_finished(self) -> bool:  # pragma: nocover, Called from forked process
        """Return whether the current process has finished running"""

        return self._states[mp.current_process().pid]

    @_process_finished.setter
    def _process_finished(self, state: bool) -> None:  # pragma: nocover, Called from forked process
        sleep(.5)  # Allow any last minute calls to finish before changing the state
        self._states[id(mp.current_process())] = state

    @property
    def pool_finished(self) -> bool:
        """Return whether all node processes have finished processing data"""

        # Check that all forked processes are finished
        return all(self._states.values())

    def start(self) -> None:
        """Start all processes asynchronously"""

        for p in self._processes:
            p.start()

    def join(self) -> None:
        """Wait for any forked processes to finish running before continuing execution"""

        for p in self._processes:
            p.join()

    def kill(self) -> None:
        """Kill all running processes without trying to exit gracefully"""

        for p in self._processes:
            p.terminate()
