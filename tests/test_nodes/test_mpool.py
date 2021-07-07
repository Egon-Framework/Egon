"""Tests for the ``MPool`` class"""

from time import sleep
from unittest import TestCase

from egon.nodes import MPool


def target_func() -> None:
    """A dummy target function"""

    sleep(2)


class ProcessAllocation(TestCase):
    """Test instances fork the correct number of processes"""

    def setUp(self) -> None:
        self.num_processes = 4
        self.pool = MPool(self.num_processes, target_func)

    def test_allocation_at_init(self) -> None:
        """Test the correct number of processes are allocated at init"""

        self.assertEqual(self.num_processes, self.pool.num_processes)
        self.assertEqual(self.num_processes, len(self.pool._processes))

    def test_error_on_negative_processes(self) -> None:
        """Assert a value error is raised when the ``num_processes`` attribute is set to a negative"""

        with self.assertRaises(ValueError):
            MPool(-1, target_func)


class Execution(TestCase):
    """Tests for the starting, running, and stopping of allocated processes"""

    def test_pool_is_finished_after_execution(self) -> None:
        """Test the ``is_finished`` property is updated after the pool executes"""

        pool = MPool(2, target_func)
        self.assertFalse(pool.is_finished(), 'Default finished state is not False.')

        pool.start()
        pool.join()

        self.assertTrue(pool.is_finished())

    def test_processes_killed_on_command(self) -> None:
        """Test processes are killed on demand"""

        pool = MPool(1, lambda *args: sleep(10))
        pool.start()
        pool.kill()
        pool.join()

        self.assertFalse(pool.is_finished())
        self.assertTrue(
            pool._processes[0].exitcode < 0,
            f'Process not ended by termination signal ({pool._processes[0].exitcode})')


class ZeroProcessPool(TestCase):
    """Tests for pool behavior with zero processes"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pool = MPool(0, target_func)

    def test_pool_is_finished_by_default(self) -> None:
        """Test the ``is_finished`` is true for a pool with zero processes"""

        self.assertTrue(MPool(0, target_func).is_finished)

    def test_run_error(self):
        """Test running the pool with zero processes raises an error"""

        with self.assertRaises(RuntimeError):
            self.pool.start()

    def test_join_error(self):
        """Test joining the pool with zero processes raises an error"""

        with self.assertRaises(RuntimeError):
            self.pool.join()

    def test_kill_error(self):
        """Test killing the pool with zero processes raises an error"""

        with self.assertRaises(RuntimeError):
            self.pool.kill()
