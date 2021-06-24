"""Tests that connector objects are able to connect together properly"""

from unittest import TestCase

from egon.connectors import BaseConnector


class ParentMapping(TestCase):
    """Test connector objects are aware of their parents"""

    def test_default_parent_is_none(self) -> None:
        """Test the connector assigned to a node returns that node as it's parent"""

        self.assertIsNone(BaseConnector().parent_node)

    def test_default_partners_is_empty(self) -> None:
        self.assertFalse(BaseConnector().partners)

    def test_default_connection_false(self) -> None:
        """Test connectors are disconnected by default"""

        self.assertFalse(BaseConnector().is_connected())
