from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import ProjectForm, PhaseForm, CostForm
from .models import Project, Phase, Cost
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('project')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': "Username already exists"
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': "Password dont match"
        })


@login_required
def project(request):
    proyectos = Project.objects.filter(user=request.user)
    return render(request, 'project.html', {'proyectito': proyectos})

@login_required
def phase(request):
    # Obtener los proyectos del usuario logueado
    proyectos = Project.objects.filter(user=request.user)   
    # Filtrar las fases que pertenecen a los proyectos del usuario logueado
    phases = Phase.objects.filter(project__in=proyectos)
    return render(request, 'phase.html', {'fases': phases})

@login_required
def cost(request):
    # Obtener los proyectos del usuario logueado
    proyectos = Project.objects.filter(user=request.user)   
    # Filtrar los costos que pertenecen a los proyectos del usuario logueado
    costos = Cost.objects.filter(project__in=proyectos)
    return render(request, 'cost.html', {'costitos': costos})

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('/')

@login_required
def createProject(request):

    if request.method == 'GET':
        return render(request, 'createproject.html', {
            'form': ProjectForm
        })

    else:
        try:
            form = ProjectForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            print(new_task)
            return redirect('project')
        except ValueError:
            return render(request, 'createproject.html', {
                'form': ProjectForm,
                'error': 'Por favor ingrese datos validos'
            })

@login_required
def createPhase(request):
    if request.method == 'GET':
        # Filtrar los proyectos por el usuario logueado
        form = PhaseForm()
        form.fields['project'].queryset = Project.objects.filter(user=request.user)
        
        return render(request, 'createphase.html', {
            'form': form
        })

    else:
        try:
            form = PhaseForm(request.POST)
            phase = form.save(commit=False)
            phase.save()
            return redirect('phase')
        except ValueError:
            return render(request, 'createphase.html', {
                'form': form,
                'error': 'Por favor ingrese datos validos'
            })
        

def load_phases(request):
    project_id = request.GET.get('project')
    phases = Phase.objects.filter(project_id=project_id).order_by('name')
    return JsonResponse(list(phases.values('id', 'name')), safe=False)

@login_required
def createCost(request):
    if request.method == 'GET':
        form = CostForm()
        form.fields['project'].queryset = Project.objects.filter(user=request.user)
        form.fields['phase'].queryset = Phase.objects.none()  # No mostrar ninguna fase hasta que se seleccione un proyecto

        return render(request, 'createcost.html', {
            'form': form
        })

    else:
        try:
            form = CostForm(request.POST)
            form.fields['project'].queryset = Project.objects.filter(user=request.user)
            form.fields['phase'].queryset = Phase.objects.filter(project__user=request.user)
            new_task = form.save(commit=False)
            new_task.save()
            return redirect('cost')
        except ValueError:
            return render(request, 'createcost.html', {
                'form': form,
                'error': 'Por favor ingrese datos válidos'
            })

@login_required
def project_detail(request, project_id):
    # Intentar obtener el proyecto solo si pertenece al usuario logueado
    project = get_object_or_404(Project, pk=project_id)
    
    # Verificar si el proyecto pertenece al usuario logueado
    if project.user != request.user:
        return redirect('project')  # Redirigir a la lista de proyectos si no pertenece al usuario

    if request.method == 'GET':
        form = ProjectForm(instance=project)
        return render(request, 'project_detail.html', {
            'proyectito': project,
            'form': form
        })
    else:
        try:
            project = get_object_or_404(Project, pk=project_id, user=request.user)
            form = ProjectForm(request.POST, instance=project)
            form.save()
            return redirect('project')
        except ValueError:
            return render(request, 'project_detail.html', {
            'proyectito': project,
            'form': form,
            'error': 'Error al actualizar'
        })


@login_required
def phase_detail(request, phase_id):
    phase = get_object_or_404(Phase, pk=phase_id)
    
    # Verificar si el proyecto asociado a la fase pertenece al usuario logueado
    if phase.project.user != request.user:
        return redirect('phase')  # Redirigir a la lista de fases o mostrar un error 404

    if request.method == 'GET':
        form = PhaseForm(instance=phase)
        # Filtrar los proyectos para que solo se muestren los del usuario logueado
        form.fields['project'].queryset = Project.objects.filter(user=request.user)
        
        return render(request, 'phase_detail.html', {
            'fase': phase,
            'form': form
        })
    else:
        try:
            form = PhaseForm(request.POST, instance=phase)
            # Filtrar los proyectos nuevamente en caso de error en el formulario
            form.fields['project'].queryset = Project.objects.filter(user=request.user)
            form.save()
            return redirect('phase')
        except ValueError:
            return render(request, 'phase_detail.html', {
                'fase': phase,
                'form': form,
                'error': 'Error al actualizar'
            })


@login_required
def cost_detail(request, cost_id):
    cost = get_object_or_404(Cost, pk=cost_id)
    
    # Verificar si el proyecto asociado al costo pertenece al usuario logueado
    if cost.project.user != request.user:
        return redirect('cost')  # Redirigir a la lista de costos o mostrar un error 404

    if request.method == 'GET':
        form = CostForm(instance=cost)
        # Filtrar los proyectos para que solo muestre los asociados al usuario logueado
        form.fields['project'].queryset = Project.objects.filter(user=request.user)
        # Filtrar las fases para que solo muestre las asociadas al proyecto actual
        form.fields['phase'].queryset = Phase.objects.filter(project=cost.project)

        return render(request, 'cost_detail.html', {
            'cost': cost,
            'form': form
        })
    else:
        try:
            form = CostForm(request.POST, instance=cost)
            # Filtrar los proyectos y fases nuevamente en caso de error en el formulario
            form.fields['project'].queryset = Project.objects.filter(user=request.user)
            form.fields['phase'].queryset = Phase.objects.filter(project=cost.project)
            form.save()
            return redirect('cost')
        except ValueError:
            return render(request, 'cost_detail.html', {
                'cost': cost,
                'form': form,
                'error': 'Error al actualizar'
            })
        

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # Verificar si el proyecto pertenece al usuario logueado
    if project.user != request.user:
        return redirect('project')  # Redirigir a la lista de proyectos si no pertenece al usuario
    
    if request.method == 'POST':
        project.delete()
        return redirect('project')


@login_required
def delete_phase(request, phase_id):
    phase = get_object_or_404(Phase, pk=phase_id)

    # Verificar si el proyecto asociado a la fase pertenece al usuario logueado
    if phase.project.user != request.user:
        return redirect('phase')  # Redirigir a la lista de fases o mostrar un error 404
    
    if request.method == 'POST':
        phase.delete()
        return redirect('phase')


@login_required
def delete_cost(request, cost_id):
    cost = get_object_or_404(Cost, pk=cost_id)

    # Verificar si el proyecto asociado al costo pertenece al usuario logueado
    if cost.project.user != request.user:
        return redirect('cost')  # Redirigir a la lista de costos o mostrar un error 404
    
    if request.method == 'POST':
        cost.delete()
        return redirect('cost')

        
