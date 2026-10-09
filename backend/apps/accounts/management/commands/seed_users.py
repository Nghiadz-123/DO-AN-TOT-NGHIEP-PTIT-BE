from django.core.management.base import BaseCommand
from apps.accounts.models import User


DEMO_USERS = [
    {
        'email': 'candidate@demo.com',
        'full_name': 'Nguyen Van An',
        'password': '123456',
        'role': User.CANDIDATE,
        'phone': '0912 345 678',
    },
    {
        'email': 'recruiter@demo.com',
        'full_name': 'Tran Thi Binh',
        'password': '123456',
        'role': User.RECRUITER,
        'company_name': 'TechViet Solutions',
        'phone': '0987 654 321',
    },
    {
        'email': 'admin@demo.com',
        'full_name': 'Admin He Thong',
        'password': '123456',
        'role': User.ADMIN,
        'is_staff': True,
        'is_superuser': True,
    },
]


class Command(BaseCommand):
    help = 'Tao du lieu mau (3 tai khoan demo: candidate, recruiter, admin)'

    def handle(self, *args, **options):
        created = 0
        for data in DEMO_USERS:
            email = data['email']
            if User.objects.filter(email=email).exists():
                self.stdout.write(f'  Da ton tai: {email}')
                continue
            is_staff = data.pop('is_staff', False)
            is_superuser = data.pop('is_superuser', False)
            password = data.pop('password')
            user = User(**data)
            user.set_password(password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            created += 1
            self.stdout.write(self.style.SUCCESS(f'  Da tao: {email} [{data["role"]}]'))

        self.stdout.write(self.style.SUCCESS(f'\nHoan thanh: tao {created} tai khoan moi.'))
        self.stdout.write('\nTai khoan demo (mat khau 123456):')
        self.stdout.write('  candidate@demo.com  - Ung vien')
        self.stdout.write('  recruiter@demo.com  - Nha tuyen dung')
        self.stdout.write('  admin@demo.com      - Admin')
