from django.db.models.signals import post_save
from django.dispatch import receiver

from authentification.models import CustomUser, NPOManagerProfile, VolunteerProfile

@receiver(post_save, sender=CustomUser)
def create_user_role_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'VOLUNTEER':
            VolunteerProfile.objects.create(user=instance.user)
        elif instance.role == 'NPO_MANAGER':
            NPOManagerProfile.objects.create(user=instance.user)
