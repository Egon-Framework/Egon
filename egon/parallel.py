from __future__ import annotations

from time import sleep
from typing import List, Optional

import ray
from ray import ObjectRef


class Actor:

    def __init__(self, fun: callable) -> None:
        self._fun = fun

    @ray.remote
    def _act(self) -> None:
        return self._fun()

    def act(self) -> None:
        return self._act.remote(self)


class MPool:
    """A pool of processes assigned to a single target function"""

    def __init__(self, num_processes: int, target: callable) -> None:
        """Create a collection of processes assigned to execute a given callable

        Args:
            num_processes: The number of processes to allocate
            target: The function to be executed by the allocated processes
        """

        if num_processes <= 0:
            raise ValueError(f'Cannot instantiate less than one processes in a pool (got {num_processes}).')

        self._num_processes = num_processes
        self._actor = Actor(target)
        self._pool: Optional[List[ObjectRef]] = None

    @property
    def num_processes(self) -> int:
        """The number of processes assigned to the pool"""

        return self._num_processes

    def is_started(self) -> bool:
        """Return whether the ``start`` method has already been called"""

        return self._pool is not None

    def is_finished(self) -> bool:
        """Return whether all processes have finished executing"""

        return self.is_started() and all(remote.future().done() for remote in self._pool)

    def start(self) -> None:
        """Start all processes asynchronously"""

        if self.is_started():
            raise RuntimeError('Pool was already started')

        self._pool = [self._actor.act() for _ in range(self._num_processes)]

    def join(self) -> None:
        """Wait for any running pool processes to finish running before continuing execution"""

        if not self.is_started() or self.is_finished():
            raise RuntimeError('Pool is not running')

        for remote in self._pool:
            ray.get(remote)

    def kill(self) -> None:
        """Kill all running processes without trying to exit gracefully"""

        if self._pool_future is None or self._pool_future.ready():
            raise RuntimeError('Pool is not running')

        self._pool.terminate()
        sleep(1)
