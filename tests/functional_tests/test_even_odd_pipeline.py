"""Test package behavior against a pipeline with multiple inputs/outputs.

This test builds and executes a modified version of an ETL pipeline.
Unlike a traditional ETL, there are two extract nodes, a single transform
node, and two load nodes.

A list of nodes are as follows:

1. The two extract nodes fetches even/odd integers from a global queue
2. The transform node separates odd and even numbers into different outputs
3. The load steps put even/odd numbers into separate global queues
"""

from multiprocessing import Queue
from queue import Empty
from unittest import TestCase

from egon import Node, Pipeline

# Input queues for feeding even/odd numbers into the pipeline
EVEN_INPUT_QUEUE = Queue()
ODD_INPUT_QUEUE = Queue()

# Output queues for collecting pipeline results
EVEN_OUTPUT_QUEUE = Queue()
ODD_OUTPUT_QUEUE = Queue()

# Populate the input queue with test values
EVEN_INPUT_VALUES = list(range(0, 10, 2))
for i in EVEN_INPUT_VALUES:
    EVEN_INPUT_QUEUE.put(i)

ODD_INPUT_VALUES = list(range(1, 10, 2))
for i in ODD_INPUT_VALUES:
    ODD_INPUT_QUEUE.put(i)


class EvenNumberGenerator(Node):
    """Pipeline node for generating even integers"""

    def __init__(self, num_processes: int = 1) -> None:
        """Define a pipeline node with a single output"""

        super().__init__(num_processes=num_processes)
        self.output = self.create_output()

    def action(self) -> None:
        """Populate the node output with even integers"""

        while True:
            try:
                self.output.put(EVEN_INPUT_QUEUE.get(timeout=2))

            except Empty:
                break


class OddNumberGenerator(Node):
    """Pipeline node for generating odd integers"""

    def __init__(self, num_processes: int = 1) -> None:
        """Define a pipeline node with a single output"""

        super().__init__(num_processes=num_processes)
        self.output = self.create_output()

    def action(self) -> None:
        """Populate the node output with odd integers"""

        while True:
            try:
                self.output.put(ODD_INPUT_QUEUE.get(timeout=2))

            except Empty:
                break


class NumberSorter(Node):
    """Sort numbers into different outputs depending on whether they are odd or even"""

    def __init__(self, num_processes: int = 1) -> None:
        """Define """

        super().__init__(num_processes=num_processes)
        self.input = self.create_input()
        self.even_output = self.create_output('Even Numbers')
        self.odd_output = self.create_output('Odd Numbers')

    def action(self) -> None:
        """Sort numbers into odds and evens"""

        for val in self.input.iter_get():
            if val % 2:
                self.odd_output.put(val)

            else:
                self.even_output.put(val)


class EvenNumberCollector(Node):
    """Load even numbers into a global queue"""

    def __init__(self, num_processes: int = 1) -> None:
        """Define a pipeline node with a single input"""

        super().__init__(num_processes=num_processes)
        self.input = self.create_input()

    def action(self) -> None:
        """Load pipeline values into the ``EVEN_OUTPUT_QUEUE`` collection"""

        for val in self.input.iter_get():
            EVEN_OUTPUT_QUEUE.put(val)


class OddNumberCollector(Node):
    """Load odd numbers into a global queue"""

    def __init__(self, num_processes: int = 1) -> None:
        """Define a pipeline node with a single input"""

        super().__init__(num_processes=num_processes)
        self.input = self.create_input()

    def action(self) -> None:
        """Load pipeline values into the ``ODD_OUTPUT_QUEUE`` collection"""

        for val in self.input.iter_get():
            ODD_OUTPUT_QUEUE.put(val)


class EvenOddPipeline(Pipeline):
    """A pipeline for generating and then adding numbers"""

    def __init__(self) -> None:
        """Instantiate a three node, ETL style pipeline"""

        super().__init__()

        # Instantiate nodes with a variety of different process counts
        self.odd_generator = self.create_node(OddNumberGenerator, num_processes=2)
        self.even_generator = self.create_node(EvenNumberGenerator, num_processes=2)
        self.sorter = self.create_node(NumberSorter, num_processes=3)
        self.even_collector = self.create_node(EvenNumberCollector, num_processes=1)
        self.odd_collector = self.create_node(OddNumberCollector, num_processes=1)

        # Connect nodes together
        self.odd_generator.output.connect(self.sorter.input)
        self.even_generator.output.connect(self.sorter.input)
        self.sorter.even_output.connect(self.even_collector.input)
        self.sorter.odd_output.connect(self.odd_collector.input)


class TestPipelineThroughput(TestCase):
    """Test data is successfully passed through the entire pipeline"""

    def runTest(self) -> None:
        """Test all input values are present in the pipeline output"""

        EvenOddPipeline().run()

        even_numbers = []
        while EVEN_OUTPUT_QUEUE.qsize() != 0:
            even_numbers.append(EVEN_OUTPUT_QUEUE.get())

        self.assertCountEqual(EVEN_INPUT_VALUES, even_numbers)

        odd_numbers = []
        while ODD_OUTPUT_QUEUE.qsize() != 0:
            odd_numbers.append(ODD_OUTPUT_QUEUE.get())

        self.assertCountEqual(ODD_INPUT_VALUES, odd_numbers)
