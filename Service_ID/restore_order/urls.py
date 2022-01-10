from django.urls import path
from . import views
from .views import SelectCandidates, ConfirmCandidates, ValidateCandidates, RegisterCandidates
from .views import ReadyToLoadPapers, LoadPapers

app_name = 'restore_order'

urlpatterns = [
    path('', views.index, name='index'),
    path('select_candidates/<str:area_name>/', SelectCandidates.as_view(), name='select_candidates'),
    path('confirm_candidates/', ConfirmCandidates.as_view(), name='confirm_candidates'),
    path('validate_candidates/', ValidateCandidates.as_view(), name='validate_candidates'),
    path('register_candidates/', RegisterCandidates.as_view(), name='register_candidates'),
    # ----------
    path('ready_to_load_papers/<str:area_name>/', ReadyToLoadPapers.as_view(), name='ready_to_load_papers'),
    path('load_papers/', LoadPapers.as_view(), name='load_papers'),
]
