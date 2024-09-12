from django.urls import path
from .views import ProjectSummaryView, ProjectPrueba

urlpatterns = [
    path('project-summary/', ProjectPrueba.as_view(), name='project_summary'),
    path('phase-summary/', ProjectSummaryView.as_view(), name='phase_summary'),
]
