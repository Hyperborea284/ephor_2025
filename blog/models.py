from django.db import models
from django.contrib.auth.models import User

class FlaskInstance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuário que criou a instância
    container_id = models.CharField(max_length=100, blank=True, null=True)  # ID do container Docker
    name = models.CharField(max_length=200)  # Nome da instância
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação
    updated_at = models.DateTimeField(auto_now=True)  # Data de atualização

    def __str__(self):
        return self.name