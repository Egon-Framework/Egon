"""Test suite for the Egon package."""

import logging
import unittest
import warnings

import ray

OLD_TEST_RUN = unittest.result.TestResult.startTestRun


def startTestRun(self) -> None:
    """Instantiate ray so test can be run against a mock ray cluster"""

    # Block resource warnings raised by a bug in some ray versions
    # See https://github.com/ray-project/ray/issues/9546
    warnings.filterwarnings('ignore', category=ResourceWarning, module='ray')

    ray.init(num_cpus=4, logging_level=logging.ERROR)


unittest.result.TestResult.startTestRun = startTestRun
