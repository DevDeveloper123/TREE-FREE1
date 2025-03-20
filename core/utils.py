from django.contrib import messages

def award_coins_for_planting(request, planting_request, coins_per_tree=10):
    """
    Начисляет коины пользователю за посадку деревьев
    
    Args:
        request: Объект запроса Django (или None, если вызывается без контекста запроса)
        planting_request: Экземпляр модели TreePlantingRequest
        coins_per_tree: Количество коинов за одно дерево
    """
    user = planting_request.user
    trees_count = planting_request.quantity
    coins_to_award = trees_count * coins_per_tree
    
    try:
        # Проверяем существование профиля
        if hasattr(user, 'profile'):
            # Начисляем коины
            user.profile.coins += coins_to_award
            user.profile.save()
            
            # Добавляем уведомление, если есть объект request
            if request:
                messages.success(
                    request, 
                    f'Начислено {coins_to_award} коинов за посадку {trees_count} деревьев!'
                )
            
            print(f"Начислено {coins_to_award} коинов пользователю {user.username}")
            return coins_to_award
        else:
            print(f"Ошибка: у пользователя {user.username} отсутствует профиль")
            return 0
    except Exception as e:
        print(f"Ошибка при начислении коинов: {str(e)}")
        return 0