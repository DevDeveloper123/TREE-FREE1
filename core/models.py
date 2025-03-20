from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class TreeType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название дерева")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='tree_types/', verbose_name="Изображение")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Вид дерева"
        verbose_name_plural = "Виды деревьев"

class PlantingSite(models.Model):
    SITE_TYPES = (
        ('yard', 'Мой двор'),
        ('public', 'Территория, требующая улучшения')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planting_sites')
    site_type = models.CharField(max_length=10, choices=SITE_TYPES, verbose_name="Тип участка")
    image = models.ImageField(upload_to='planting_sites/', verbose_name="Фотография")
    location = models.CharField(max_length=255, verbose_name="Локация")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_site_type_display()} - {self.user.username}"
    
    class Meta:
        verbose_name = "Участок для посадки"
        verbose_name_plural = "Участки для посадки"

class TreePlantingRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('completed', 'Завершено'),
        ('rejected', 'Отклонено')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planting_requests')
    tree_type = models.ForeignKey(TreeType, on_delete=models.CASCADE)
    planting_site = models.ForeignKey(PlantingSite, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Количество деревьев")
    price_per_tree = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за дерево")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")
    
    def __str__(self):
        return f"Запрос на посадку {self.quantity} {self.tree_type.name} от {self.user.username}"
    
    def get_total_price(self):
        """Возвращает общую стоимость запроса"""
        return self.price_per_tree * self.quantity
    
    def save(self, *args, **kwargs):
        """Переопределяем сохранение для обработки изменения статуса"""
        # Если объект уже существует и статус меняется на "Завершено"
        if self.pk and self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super(TreePlantingRequest, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Запрос на посадку"
        verbose_name_plural = "Запросы на посадку"
        ordering = ['-created_at']

class TreeServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider')
    name = models.CharField(max_length=100, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание услуги")
    contact_phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Поставщик услуг"
        verbose_name_plural = "Поставщики услуг"
