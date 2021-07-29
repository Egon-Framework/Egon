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
