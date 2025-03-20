from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RedirectAnonymousUserMiddleware:
    """
    Middleware для перенаправления незарегистрированных пользователей 
    на страницу входа при попытке доступа к защищенным разделам.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URL-пути, требующие аутентификации
        self.protected_urls = [
            '/plant-tree/',
            '/my-land/',
            '/sell-trees/'
        ]
        
        # URL-пути, к которым всегда разрешен доступ
        self.public_urls = [
            '/',
            '/auth/login/',
            '/auth/register/',
            '/admin/',
        ]
    
    def __call__(self, request):
        # Если пользователь не аутентифицирован и пытается получить доступ к защищенному URL
        if not request.user.is_authenticated:
            current_path = request.path_info
            
            # Проверяем, является ли текущий URL защищенным
            if any(current_path.startswith(url) for url in self.protected_urls):
                messages.info(request, 'Пожалуйста, войдите в свой аккаунт для продолжения.')
                return redirect(f"{reverse('login')}?next={current_path}")
        
        response = self.get_response(request)
        return response