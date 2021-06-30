"""Tests for the ``BaseConnector`` class"""

from unittest import TestCase

from egon.connectors import BaseConnector


class DefaultState(TestCase):
    """Test connector properties are null by default"""

    def test_default_parent_is_none(self) -> None:
        """Test that a connector's parent is ``None`` by default"""

        self.assertIsNone(BaseConnector().parent_node)

    def test_default_partners_is_empty(self) -> None:
        """Test the default tuple of partners is empty"""

        self.assertIsInstance(BaseConnector().partners, tuple)
        self.assertFalse(BaseConnector().partners)

    def test_default_connection_false(self) -> None:
        """Test connectors are marked as disconnected by default"""

        self.assertFalse(BaseConnector().is_connected())
