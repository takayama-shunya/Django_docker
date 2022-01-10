from django.urls import path
from . import views
from .views import CreateServiceStock, ValidateServiceStock, RegisterServiceStock
from .views import GetNeeds, FuzzySearch, ShowServiceStock, ValidateUsedService, ConfirmUsedService, \
    RegisterUsedService

app_name = 'peace_keeping'

urlpatterns = [
    path('', views.index, name='index'),
    path('create_serv/<str:area_name>/', CreateServiceStock.as_view(), name='create_serv'),
    path('validate_serv/', ValidateServiceStock.as_view(), name='validate_serv'),
    path('register_serv/', RegisterServiceStock.as_view(), name='register_serv'),
    # -----
    path('get_needs/<str:area_name>/', GetNeeds.as_view(), name='get_needs'),
    path('fuzzy_search/<str:area_name>/<str:phrase>/', FuzzySearch.as_view(), name='get_needs'),
    path('show_serv/', ShowServiceStock.as_view(), name='show_serv'),
    path('validate_used_serv/', ValidateUsedService.as_view(), name='validate_used_serv'),
    path('confirm_used_serv/', ConfirmUsedService.as_view(), name='confirm_used_serv'),
    path('register_used_serv/', RegisterUsedService.as_view(), name='register_used_serv'),
]
