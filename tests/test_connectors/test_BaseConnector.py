"""Tests for the ``BaseConnector`` class"""

from unittest import TestCase

from egon.connectors import BaseConnector


class StringRepresentation(TestCase):
    """Tests for the representation of connector instances as strings"""

    def test_string_representation(self) -> None:
        """Test connectors include name and ID info when cast to a string"""

        connector_name = 'my_connector'
        connector = BaseConnector(connector_name)

        expected_string = f'<BaseConnector(name={connector_name}) object at {hex(id(connector))}>'
        self.assertEqual(expected_string, str(connector))
