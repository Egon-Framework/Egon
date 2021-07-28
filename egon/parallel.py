"""Utilities for running code in parallel"""

from __future__ import annotations

from time import sleep
from typing import List, Optional

import ray
from ray import ObjectRef


class Actor:
    """Worker object responsible for executing tasks a remote machine"""

    def __init__(self, fun: callable) -> None:
        """Worker object responsible for executing tasks a remote machine

        Args:
            fun: The callable to be executed by the actor
        """

        self._fun = fun

    @ray.remote
    def _act(self) -> Optional:
        return self._fun()

    def act(self) -> Optional:
        """Run the actor remotely"""

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

    def is_running(self) -> bool:
        """Return whether the ``start`` method has already been called"""

        return self._pool is not None and any(remote.future().running() for remote in self._pool)

    def start(self) -> None:
        """Start all processes asynchronously"""

        if self.is_running():
            raise RuntimeError('Pool was already started once before')

        self._pool = [self._actor.act() for _ in range(self._num_processes)]

    def join(self) -> None:
        """Wait for any running pool processes to finish running before continuing execution"""

        for remote in self._pool:
            ray.get(remote)

    def kill(self) -> None:
        """Kill all running processes without trying to exit gracefully"""

        ray.kill(self._actor)
        sleep(1)
