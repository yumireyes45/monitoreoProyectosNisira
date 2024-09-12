from django.contrib import admin
from .models import Project, Phase, Cost

# Register your models here.
admin.site.register(Project)
admin.site.register(Phase)
admin.site.register(Cost)
