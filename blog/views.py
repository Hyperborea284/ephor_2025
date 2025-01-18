from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FlaskInstance
from .forms import FlaskInstanceForm
import docker

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
                'sua-imagem-flask',  # Nome da imagem Docker da aplicação Flask
                detach=True,  # Executa o container em segundo plano
                name=f"flask-instance-{instance.pk}",  # Nome único para o container
                ports={'5000/tcp': 5000}  # Expõe a porta 5000
            )
            instance.container_id = container.id
            instance.save()
            messages.success(request, "Instância iniciada com sucesso!")
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
            instance.container_id = None
            instance.save()
            messages.success(request, "Instância parada com sucesso!")
        else:
            messages.warning(request, "A instância já está parada.")
    except docker.errors.DockerException as e:
        messages.error(request, f"Erro ao parar a instância: {e}")
    return redirect('instance_list')

@login_required
def view_instance(request, pk):
    instance = get_object_or_404(FlaskInstance, pk=pk, user=request.user)
    return render(request, 'blog/instance_view.html', {'instance': instance})