"""
Django signals to automatically update volunteer counts in State and District models
when volunteer records are created, saved, or deleted.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from models.volunteer import Volunteer
from services.volunteer_count_service import VolunteerCountService


@receiver(post_save, sender=Volunteer)
def update_counts_on_volunteer_save(sender, instance, created, **kwargs):
    """
    Signal receiver to update state and district volunteer counts
    when a volunteer is created or updated.
    
    Args:
        sender: The model class (Volunteer)
        instance: The volunteer instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments
    """
    if instance.state_id:
        VolunteerCountService.update_volunteer_count(state_id=instance.state_id)
    
    if instance.district_id:
        VolunteerCountService.update_volunteer_count(district_id=instance.district_id)


@receiver(post_delete, sender=Volunteer)
def update_counts_on_volunteer_delete(sender, instance, **kwargs):
    """
    Signal receiver to update state and district volunteer counts
    when a volunteer is deleted.
    
    Args:
        sender: The model class (Volunteer)
        instance: The volunteer instance being deleted
        **kwargs: Additional keyword arguments
    """
    if instance.state_id:
        VolunteerCountService.update_volunteer_count(state_id=instance.state_id)
    
    if instance.district_id:
        VolunteerCountService.update_volunteer_count(district_id=instance.district_id)
