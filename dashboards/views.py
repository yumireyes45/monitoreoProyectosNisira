from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .dash_apps.finished_apps.phase_dashboard import funcionDash
from .dash_apps.finished_apps.project_dashboard import funcionDashPrueba  # Importar la función, no 'app'
from tasks.models import Project
import pandas as pd 
import uuid

class ProjectPrueba(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/project_summary.html'
    
    def get(self, request, *args, **kwargs):
        code = str(uuid.uuid4())  # Generar un código único para la instancia de Dash
        proyectos = Project.objects.filter(user=self.request.user)

        # Convertir el QuerySet de proyectos a un DataFrame
        df_proyectos = pd.DataFrame(list(proyectos.values()))

        context = {

            'dashboard': funcionDashPrueba(code, df_proyectos.to_dict('records')),  # Pasa el código a la función Dash
            'code': code
        }
        return render(request, self.template_name, context)

class ProjectSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/project_summary.html'
    
    def get(self, request, *args, **kwargs):
        code = str(uuid.uuid4())  # Generar un código único para la instancia de Dash
        proyectos = Project.objects.filter(user=self.request.user)

        # Convertir el QuerySet de proyectos a un DataFrame
        df_proyectos = pd.DataFrame(list(proyectos.values()))

        context = {

            'dashboard': funcionDash(code, df_proyectos.to_dict('records')),  # Pasa el código a la función Dash
            'code': code
        }
        return render(request, self.template_name, context)
