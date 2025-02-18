from django.db import models
from django.contrib.auth.models import User
import uuid

class FlaskInstance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuário que criou a instância
    container_id = models.CharField(max_length=100, blank=True, null=True)  # ID do container Docker
    name = models.CharField(max_length=200)  # Nome da instância (fornecido pelo usuário)
    unique_name = models.CharField(max_length=250, unique=True, blank=True, null=True)  # Nome único do container
    port = models.IntegerField(blank=True, null=True)  # Porta aleatória escolhida dinamicamente
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação
    updated_at = models.DateTimeField(auto_now=True)  # Data de atualização

    def save(self, *args, **kwargs):
        if not self.unique_name:
            unique_id = str(uuid.uuid4())[:8]  # Gerando um identificador único de 8 caracteres
            self.unique_name = f"{self.name}-{unique_id}"  # Nome único preservando o nome do usuário
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
