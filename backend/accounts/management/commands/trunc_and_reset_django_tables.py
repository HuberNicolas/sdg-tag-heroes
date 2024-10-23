from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
from django.db.models.signals import post_migrate
from backend.accounts.signals import create_initial_users

class Command(BaseCommand):
    help = "Truncate non-core Django-related tables and reapply migrations."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Truncating non-core Django-related tables..."))

        # Fetch the list of all tables managed by Django
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()

            # List the tables you want to truncate (custom models)
            data_tables = [
                'accounts_admin',
                'accounts_customuser',
                'accounts_customuser_groups',
                'accounts_customuser_user_permissions',
                'accounts_expert',
                'accounts_labeler',
            ]

            # Disable foreign key checks to prevent issues while truncating tables
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

            for table in data_tables:
                if table in tables:
                    self.stdout.write(self.style.WARNING(f"Truncating table: {table}"))
                    cursor.execute(f"TRUNCATE TABLE `{table}`;")

            # Re-enable foreign key checks after truncating tables
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

        self.stdout.write(self.style.SUCCESS("Non-core Django-related tables truncated successfully!"))

        # Temporarily disable the post_migrate signal to avoid user creation before the tables exist
        self.stdout.write(self.style.WARNING("Disabling post_migrate signals temporarily..."))
        post_migrate.disconnect(create_initial_users, dispatch_uid="create_initial_users")

        # Run migrations to ensure all tables are properly structured
        self.stdout.write(self.style.WARNING("Running migrations..."))
        call_command('migrate')

        # Reconnect the post_migrate signal to re-enable user creation
        self.stdout.write(self.style.WARNING("Re-enabling post_migrate signals..."))
        post_migrate.connect(create_initial_users, dispatch_uid="create_initial_users")

        self.stdout.write(self.style.SUCCESS("Migrations completed and signals re-enabled!"))
