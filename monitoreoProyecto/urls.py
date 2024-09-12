"""
URL configuration for monitoreoProyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tasks import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name='home'),
    path("signup/", views.signup, name='signup'),
    path("project/", views.project, name='project'),
    path("phases/", views.phase, name='phase'),
    path("costs/", views.cost, name='cost'),
    path("logout/", views.signout, name='logout'),
    path("signin/", views.signin, name='signin'),
    path("project/create/", views.createProject, name='projectcreate'),
    path("phase/create/", views.createPhase, name='phasecreate'),
    path("cost/create/", views.createCost, name='costcreate'),
    path('ajax/load-phases/', views.load_phases, name='ajax_load_phases'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('phases/<int:phase_id>/', views.phase_detail, name='phase_detail'),
    path('costs/<int:cost_id>/', views.cost_detail, name='cost_detail'),
    path('project/<int:project_id>/delete', views.delete_project, name='delete_project'),
    path('phases/<int:phase_id>/delete', views.delete_phase, name='delete_phase'),
    path('costs/<int:cost_id>/delete', views.delete_cost, name='delete_cost'),
    # Incluir las URLs de la app 'dashboards'
    path('dashboards/', include('dashboards.urls'), name='dashboard1'),
    # Incluir las URLs de django_plotly_dash
    path('django_plotly_dash/', include('django_plotly_dash.urls')),

]
