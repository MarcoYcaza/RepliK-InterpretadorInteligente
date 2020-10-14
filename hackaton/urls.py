from django.urls import path
from . import views

urlpatterns = [
    path('intelligent-interpreter-solution',views.uploadDocument,name='hackaton-hackaton'),
    path('download-database',views.download,name='hackaton-download'),
    path('retrieve-info',views.retrieveInformation,name='hackaton-retrieve-info'),
]
