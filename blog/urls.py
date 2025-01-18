from django.urls import path
from . import views

urlpatterns = [
    path('', views.instance_list, name='instance_list'),  # Lista de instâncias
    path('create/', views.create_instance, name='create_instance'),  # Criar instância
    path('start/<int:pk>/', views.start_instance, name='start_instance'),  # Iniciar instância
    path('stop/<int:pk>/', views.stop_instance, name='stop_instance'),  # Parar instância
    path('view/<int:pk>/', views.view_instance, name='view_instance'),  # Visualizar instância
]