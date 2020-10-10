from django.urls import path
from . import views

urlpatterns = [
    path('intelligent-interpreter-solution',views.uploadDocument,name='hackaton-hackaton')   
]
