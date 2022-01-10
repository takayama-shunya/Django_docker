from django.urls import path
from . import views
from .views import MergeAreaCsv
app_name = 'offices'
urlpatterns = [
    path('', views.index, name='index'),
    path('merge_area_csv', MergeAreaCsv.as_view(), name='merge_area_csv'),
]
