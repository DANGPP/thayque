from django.core.management.base import BaseCommand
from app.models import Staff


class Command(BaseCommand):
    help = 'Create default admin user'

    def handle(self, *args, **options):
        if not Staff.objects.filter(username='admin').exists():
            Staff.objects.create_superuser(
                username='admin',
                email='admin@bookstore.vn',
                password='admin123',
                role='admin',
                first_name='Admin',
                last_name='BookStore'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
