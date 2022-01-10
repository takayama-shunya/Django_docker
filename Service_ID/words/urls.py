from django.urls import path
from . import views
from .views import MergeWords, UpdateWords, SetIsStandard, ValidateIsStandard

app_name = 'words'
urlpatterns = [
    path('', views.index, name='index'),
    path('merge_words/<str:key>/', MergeWords.as_view(), name='merge_words'),
    path('update_words/<str:key>/', UpdateWords.as_view(), name='update_words'),
    path('set_is_standard/<str:key>/', SetIsStandard.as_view(), name='set_is_standard'),
    path('register_is_standard/<str:key>/', ValidateIsStandard.as_view(), name='register_is_standard'),
    path('is_standard_registered/', views.registered_is_standard, name='is_standard_registered'),
]
