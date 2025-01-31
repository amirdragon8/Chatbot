from django.db import models
from authentification.models import CustomUser

# Create your models here.
  

class Task(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the task")
    description = models.TextField(help_text="Description of the task")
    start_date = models.DateField(help_text="Start date of the task(YYYY-MM-DD)")
    end_date = models.DateField(help_text="End date of the task(YYYY-MM-DD)")
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tasks",
        help_text="The user who created the task"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the task was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the task was last updated")

    def __str__(self):
        return f"{self.name} (Owner: {self.created_by.username})"

