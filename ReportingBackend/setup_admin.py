import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReportingBackend.settings.prod')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin user already exists (using email since your model uses email as username)
if not User.objects.filter(email='admin@gmail.com', is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@gmail.com',
        password='admin123'
    )
    print('Admin user created successfully')
else:
    print('Admin user already exists')