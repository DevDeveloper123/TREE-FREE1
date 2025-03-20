from django.urls import path
from . import views

urlpatterns = [
    # Главная страница и личный кабинет
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Раздел "Я хочу посадить дерево"
    path('plant-tree/', views.plant_tree, name='plant_tree'),
    path('plant-tree/select-tree-type/', views.select_tree_type, name='select_tree_type'),
    path('plant-tree/select-planting-site/', views.select_planting_site, name='select_planting_site'),
    path('plant-tree/set-tree-price/', views.set_tree_price, name='set_tree_price'),
    path('plant-tree/set-tree-quantity/', views.set_tree_quantity, name='set_tree_quantity'),
    
    # Раздел "У меня есть участок для посадки деревьев"
    path('my-land/', views.my_land, name='my_land'),
    path('my-land/add-planting-site/', views.add_planting_site, name='add_planting_site'),
    path('my-land/select-tree-type/', views.land_select_tree_type, name='land_select_tree_type'),
    path('my-land/set-tree-price/', views.land_set_tree_price, name='land_set_tree_price'),
    path('my-land/set-tree-quantity/', views.land_set_tree_quantity, name='land_set_tree_quantity'),
    
    # Раздел "Продаю и сажаю деревья"
    path('sell-trees/', views.sell_trees, name='sell_trees'),
    path('service-provider-profile/', views.service_provider_profile, name='service_provider_profile'),
    path('service-providers/', views.service_providers_list, name='service_providers_list'),
    path('contact-provider/<int:provider_id>/', views.contact_provider, name='contact_provider'),
    
    # Управление запросами на посадку
    path('planting-requests/', views.planting_requests, name='planting_requests'),
    path('planting-request/<int:request_id>/', views.planting_request_detail, name='planting_request_detail'),
    path('planting-request/<int:request_id>/cancel/', views.cancel_planting_request, name='cancel_planting_request'),
    path('planting-request/<int:request_id>/complete/', views.complete_planting_request, name='complete_planting_request'),
    
    # Управление участками
    path('planting-sites/', views.planting_sites, name='planting_sites'),
]