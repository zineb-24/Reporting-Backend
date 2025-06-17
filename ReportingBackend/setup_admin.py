import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReportingBackend.settings.prod')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@gmail.com',
        password='admin123'
    )
    print('Admin user created successfully')
else:
    print('Admin user already exists')