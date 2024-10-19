"""
Django command to wait until the database has become available.
"""

from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as PsycopgOperationalError
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to wait until the database has become available."""

    def handle(self, *args, **options):
        """Entry point of the management command."""
        self.stdout.write('Waiting for database connection...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (PsycopgOperationalError, OperationalError) as e:
                self.stdout.write('Database connection failed. Waiting 1 second')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database connection successful.'))