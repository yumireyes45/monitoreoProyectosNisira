from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Phase(models.Model):
    status_choices = (
    ("notcompleted", "No iniciado"),
    ("completed", "Completado"),
    ("progres", "En proceso"),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    important = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=status_choices)
    percentage_completed = models.DecimalField(max_digits=5, decimal_places=2)
    duration_hours = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
class Cost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cost de {self.amount} para {self.project.name}"



    