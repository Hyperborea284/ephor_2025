from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FlaskInstance
from .forms import FlaskInstanceForm
import docker
import random
import socket

# Função auxiliar para encontrar uma porta disponível dinamicamente
def get_available_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))  # Deixa o sistema operacional escolher uma porta disponível
    _, port = sock.getsockname()
    sock.close()
    return port

def landing_page(request):
    return render(request, 'landing_page.html')

@login_required
def instance_list(request):
    instances = FlaskInstance.objects.filter(user=request.user)
    return render(request, 'blog/instance_list.html', {'instances': instances})

@login_required
def create_instance(request):
    if request.method == 'POST':
        form = FlaskInstanceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.port = get_available_port()  # Define a porta disponível dinamicamente
            instance.save()
            messages.success(request, "Instância criada com sucesso!")
            return redirect('instance_list')
    else:
        form = FlaskInstanceForm()
    return render(request, 'blog/instance_form.html', {'form': form})

@login_required
def start_instance(request, pk):
    try:
        client = docker.from_env()
        instance = get_object_or_404(FlaskInstance, pk=pk, user=request.user)

        if not instance.container_id:
            container = client.containers.run(
                'sua-imagem-flask',  # Nome da imagem do container Flask
                detach=True,  # Executa em segundo plano
                name=instance.unique_name,  # Nome único do container
                ports={'5000/tcp': instance.port}  # Mapeia a porta 5000 do container para uma porta única na máquina host
            )
            instance.container_id = container.id
            instance.save()
            messages.success(request, f"Instância iniciada com sucesso na porta {instance.port}!")
        else:
            messages.warning(request, "A instância já está em execução.")

    except docker.errors.DockerException as e:
        messages.error(request, f"Erro ao iniciar a instância: {e}")

    return redirect('instance_list')

@login_required
def stop_instance(request, pk):
    try:
        client = docker.from_env()
        instance = get_object_or_404(FlaskInstance, pk=pk, user=request.user)

        if instance.container_id:
            container = client.containers.get(instance.container_id)
            container.stop()
            container.remove()  # Remove o container após parar
            instance.container_id = None
            instance.port = None  # Libera a porta para futuros usos
            instance.save()
            messages.success(request, "Instância parada e removida com sucesso!")
        else:
            messages.warning(request, "A instância já está parada.")

    except docker.errors.DockerException as e:
        messages.error(request, f"Erro ao parar a instância: {e}")

    return redirect('instance_list')

@login_required
def view_instance(request, pk):
    instance = get_object_or_404(FlaskInstance, pk=pk, user=request.user)
    return render(request, 'blog/instance_view.html', {'instance': instance})
