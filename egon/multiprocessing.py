"""Utilities for managing parallel execution, including process pools and queues."""

from __future__ import annotations

import logging
import multiprocessing as mp
import uuid


class EgonProcess(mp.Process):

    def __init__(self, *args, **kwargs) -> None:
        super(EgonProcess, self).__init__(*args, **kwargs)
        self.egon_id = uuid.uuid4()


class MultiprocessingEngine:
    """A processes pool for executing callable objects in parallel

    The ``MultiprocessingEngine`` class is much less general than the built-in
    ``Pool`` object. For example, instances are tied to a single callable
    object defined at init and cannot be dynamically mapped to other callables
    (i.e., there are no `map`` or ``apply`` methods).
    """

    def __init__(self, num_processes: int, target: callable) -> None:
        """Create a new engine instance for evaluating the given callable

        Args:
            num_processes: The number of processes to run in parallel
            target: The callable object to be executed in parallel
        """

        self._target = target
        self._processes = []  # Collection of processes managed by the parent instance
        self._states = mp.Manager().dict()  # Map process memory id to process execution state

        self._locked = False
        self.set_num_processes(num_processes)

    def _wrap_target(self) -> None:  # pragma: nocover - this method called from child process
        """Wrapper method for calling the target function and updating process status"""

        self._target()

        current_id = mp.current_process().pid
        for process in self._processes:
            if process.pid == current_id:
                self._states[process.egon_id] = True
                break

    def reset(self) -> None:
        """Reset the engine instance so it can be reused

        Raises:
            RuntimeError: When resetting an engine before it has finished executing
        """

        if not self.is_finished():
            raise RuntimeError('Some processes have not finished executing')

        self._locked = False
        self.set_num_processes(self.get_num_processes())

    def get_num_processes(self) -> int:
        """Return the number of processes assigned to the pool"""

        return len(self._processes)

    def set_num_processes(self, num_processes: int) -> None:
        """Modify the number of processes assigned to the pool

        Args:
            num_processes: The number of processes to allocate

        Raises:
            RuntimeError: When modifying an engine that has already been started
            ValueError: When the number of processes is invalid
        """

        if self._locked:
            raise RuntimeError('Cannot modify the number of processes once an engine has been started')

        if num_processes <= 0:
            raise ValueError('Number of processes must be greater than zero')

        self._processes = [EgonProcess(target=self._wrap_target) for _ in range(num_processes)]
        self._states = mp.Manager().dict({p.egon_id: False for p in self._processes})

    def is_finished(self) -> bool:
        """Return whether all processes in the pool have exited execution"""

        logging.debug(f'engine states: {self._states}')
        return all(self._states.values())

    def run(self) -> None:
        """Start all processes and join them to the current process"""

        self.run_async()
        self.join()

    def run_async(self) -> None:
        """Start all processes asynchronously"""

        self._locked = True
        for p in self._processes:
            p.start()

    def join(self) -> None:
        """Wait for any running processes to exit before continuing execution"""

        for p in self._processes:
            p.join()

    def kill(self) -> None:
        """Kill all running processes without attempting to exit gracefully"""

        for p in self._processes:
            p.kill()
            self._states[p.egon_id] = True
