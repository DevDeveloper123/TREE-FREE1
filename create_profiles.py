from django.contrib.auth.models import User
from authentication.models import UserProfile

def create_profiles():
    users_without_profile = []
    for user in User.objects.all():
        try:
            # Проверяем, существует ли профиль
            profile = user.profile
        except User.profile.RelatedObjectDoesNotExist:
            # Если профиля нет, создаем его
            users_without_profile.append(user.username)
            UserProfile.objects.create(user=user)
    
    return users_without_profile

if __name__ == "__main__":
    created_for = create_profiles()
    print(f"Профили созданы для пользователей: {', '.join(created_for)}")