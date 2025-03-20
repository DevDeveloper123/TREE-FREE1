from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Расширенная модель пользователя с дополнительными полями"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    coins = models.PositiveIntegerField(default=0, verbose_name="Монеты")
    
    def __str__(self):
        return f"Профиль пользователя {self.user.username}"
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

# Создание профиля автоматически при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
