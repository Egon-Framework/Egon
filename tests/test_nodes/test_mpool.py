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
        self.assertFalse(pool.is_finished())

        pool.join()
        self.assertTrue(pool.is_finished())

    def test_processes_killed_on_command(self) -> None:
        """Test processes are killed on demand"""

        pool = MPool(1, lambda *args: sleep(10))
        pool.start()
        pool.kill()

        self.assertTrue(pool.is_finished())
