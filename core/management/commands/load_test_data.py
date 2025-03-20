import os
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from core.models import TreeType, PlantingSite, TreePlantingRequest, TreeServiceProvider

class Command(BaseCommand):
    help = 'Загружает тестовые данные для платформы Tree Free'

    def handle(self, *args, **kwargs):
        self.stdout.write('Загрузка тестовых данных...')
        
        # Создаем тестового пользователя, если его нет
        if not User.objects.filter(username='testuser').exists():
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpassword',
                first_name='Тест',
                last_name='Пользователь'
            )
            self.stdout.write(self.style.SUCCESS(f'Создан тестовый пользователь: {test_user.username}'))
        else:
            test_user = User.objects.get(username='testuser')
            self.stdout.write(f'Тестовый пользователь уже существует: {test_user.username}')
        
        # Создаем тестовые виды деревьев
        tree_types_data = [
            {
                'name': 'Дуб',
                'description': 'Мощное долговечное дерево с характерными листьями и желудями. Может жить до 500 лет.',
                'image_path': 'core/test_data/oak.jpg'
            },
            {
                'name': 'Береза',
                'description': 'Элегантное дерево с белой корой и нежными листьями. Символ русской природы.',
                'image_path': 'core/test_data/birch.jpg'
            },
            {
                'name': 'Сосна',
                'description': 'Вечнозеленое хвойное дерево, хорошо растет на песчаных почвах.',
                'image_path': 'core/test_data/pine.jpg'
            },
            {
                'name': 'Клен',
                'description': 'Красивое дерево с резными листьями, осенью приобретающими яркую окраску.',
                'image_path': 'core/test_data/maple.jpg'
            },
            {
                'name': 'Яблоня',
                'description': 'Плодовое дерево, дающее красивые цветы весной и вкусные плоды осенью.',
                'image_path': 'core/test_data/apple.jpg'
            }
        ]
        
        # Проверяем и создаем каталог для тестовых изображений
        test_images_dir = os.path.join(settings.BASE_DIR, 'media', 'test_images')
        os.makedirs(test_images_dir, exist_ok=True)
        
        # Создаем типы деревьев
        for tree_data in tree_types_data:
            if not TreeType.objects.filter(name=tree_data['name']).exists():
                tree_type = TreeType(
                    name=tree_data['name'],
                    description=tree_data['description']
                )
                
                # Заглушка для изображения (в реальном проекте нужно будет добавить реальные изображения)
                # Здесь мы создаем пустой файл как заглушку
                image_path = os.path.join(test_images_dir, f"{tree_data['name'].lower()}.jpg")
                with open(image_path, 'w') as f:
                    f.write('Test image file')
                
                with open(image_path, 'rb') as img_file:
                    tree_type.image.save(f"{tree_data['name'].lower()}.jpg", File(img_file), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'Создан тип дерева: {tree_type.name}'))
            else:
                self.stdout.write(f'Тип дерева уже существует: {tree_data["name"]}')
        
        # Создаем тестовые участки
        site_types = ['yard', 'public']
        locations = [
            'ул. Ленина, 15, Ташкент',
            'пр. Навои, 25, Ташкент',
            'ул. Садовая, 7, Ташкент',
            'ул. Центральная, 42, Ташкент',
            'пр. Мира, 101, Ташкент'
        ]
        
        for i in range(3):
            if PlantingSite.objects.filter(user=test_user).count() < 3:
                site = PlantingSite(
                    user=test_user,
                    site_type=random.choice(site_types),
                    location=random.choice(locations)
                )
                
                # Заглушка для изображения
                image_path = os.path.join(test_images_dir, f"site_{i}.jpg")
                with open(image_path, 'w') as f:
                    f.write('Test site image file')
                
                with open(image_path, 'rb') as img_file:
                    site.image.save(f"site_{i}.jpg", File(img_file), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'Создан тестовый участок: {site.location}'))
        
        # Создаем тестовые запросы на посадку
        tree_types = TreeType.objects.all()
        sites = PlantingSite.objects.filter(user=test_user)
        statuses = ['pending', 'approved', 'completed', 'rejected']
        
        if sites.exists() and tree_types.exists():
            for i in range(5):
                if TreePlantingRequest.objects.filter(user=test_user).count() < 5:
                    request = TreePlantingRequest.objects.create(
                        user=test_user,
                        tree_type=random.choice(tree_types),
                        planting_site=random.choice(sites),
                        quantity=random.randint(1, 10),
                        price_per_tree=random.randint(1000, 5000),
                        status=random.choice(statuses)
                    )
                    self.stdout.write(self.style.SUCCESS(f'Создан тестовый запрос на посадку: {request}'))
        
        # Создаем тестового поставщика услуг
        if not TreeServiceProvider.objects.filter(user=test_user).exists():
            provider = TreeServiceProvider.objects.create(
                user=test_user,
                name='ЭкоДеревья',
                description='Предлагаем услуги по посадке и уходу за деревьями. Большой опыт работы. Выезд на участок.',
                contact_phone='+998 90 123 45 67'
            )
            self.stdout.write(self.style.SUCCESS(f'Создан тестовый поставщик услуг: {provider.name}'))
        
        self.stdout.write(self.style.SUCCESS('Загрузка тестовых данных завершена!'))