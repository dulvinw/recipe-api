from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db until db is ready"""
        with patch('django.db.utils.ConnectHandler.__getitem__') as gi:
            gi.return_value = True
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)