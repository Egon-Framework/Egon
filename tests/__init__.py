"""Test suite for the Egon package."""

import unittest

import ray

OLD_TEST_RUN = unittest.result.TestResult.startTestRun


def startTestRun(self) -> None:
    """Instantiate ray so test can be run against a mock ray cluster"""

    ray.init(num_cpus=4)


unittest.result.TestResult.startTestRun = startTestRun
