from time import sleep
from unittest import TestCase

from egon._utils import MPool


def target_func() -> None:
    sleep(2)


class ProcessAllocation(TestCase):
    """Test ``Node`` instances fork the correct number of processes"""

    def setUp(self) -> None:
        self.num_processes = 4
        self.pool = MPool(self.num_processes, target_func)

    def test_allocation_at_init(self) -> None:
        """Test the correct number of processes are allocated at init"""

        self.assertEqual(self.num_processes, self.pool.num_processes)
        self.assertEqual(self.num_processes, len(self.pool._processes))

    def test_reallocation(self) -> None:
        """Test a new set of processes are allocated when the number of processes is changed"""

        new_process_count = 2
        self.pool.num_processes = new_process_count
        self.assertEqual(new_process_count, self.pool.num_processes)
        self.assertEqual(new_process_count, len(self.pool._processes))

    def test_error_if_processes_are_alive(self) -> None:
        """Test a RuntimeError is raised when trying to reallocate processes on a running node"""

        self.pool.start()
        with self.assertRaises(RuntimeError):
            self.pool.num_processes = 1

    def test_error_on_negative_processes(self) -> None:
        """Assert a value error is raised when the ``num_processes`` attribute is set to a negative"""

        with self.assertRaises(ValueError):
            MPool(-1, target_func)

        with self.assertRaises(ValueError):
            self.pool.num_processes = -1

    def test_error_on_zero_processes(self) -> None:
        """Assert a value error is raised when the ``num_processes`` attribute is set to zero"""

        with self.assertRaises(ValueError):
            MPool(0, target_func)

        with self.assertRaises(ValueError):
            self.pool.num_processes = 0


class Execution(TestCase):

    def test_pool_is_finished_after_execution(self) -> None:
        """Test the ``pool_finished`` property is updated after the pool executes"""

        pool = MPool(2, target_func)
        self.assertFalse(pool.pool_finished, 'Default finished state is not False.')

        pool.start()
        pool.join()

        self.assertTrue(pool.pool_finished)

    def test_processes_killed_on_command(self) -> None:
        """Test processes are killed on demand"""

        pool = MPool(1, lambda *args: sleep(10))
        pool.start()
        pool.kill()
        pool.join()

        self.assertTrue(pool._processes[0].exitcode < 0, f'Process not ended by termination signal ({pool._processes[0].exitcode })')
        self.assertFalse(pool.pool_finished)
