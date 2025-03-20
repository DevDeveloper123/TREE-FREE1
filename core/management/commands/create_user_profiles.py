from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile

class Command(BaseCommand):
    help = 'Создает профили для всех пользователей, у которых их нет'

    def handle(self, *args, **kwargs):
        users_without_profile = []
        for user in User.objects.all():
            try:
                # Проверяем, существует ли профиль
                profile = user.profile
            except:
                # Если профиля нет, создаем его
                users_without_profile.append(user.username)
                UserProfile.objects.create(user=user)
        
        if users_without_profile:
            self.stdout.write(self.style.SUCCESS(f'Профили созданы для пользователей: {", ".join(users_without_profile)}'))
        else:
            self.stdout.write(self.style.SUCCESS('Все пользователи уже имеют профили'))