"""
Service to manage volunteer count updates for State and District models
When a volunteer is created/updated/deleted, this service updates the corresponding counts
"""
from django.db.models import Count
from models.volunteer import Volunteer
from models.state import State
from models.district import District


class VolunteerCountService:
    """
    Service to handle volunteer count updates for states and districts.
    Triggered when volunteers are created, updated, or deleted.
    """
    
    @staticmethod
    def update_volunteer_count(state_id=None, district_id=None):
        """
        Update volunteer count for a specific state or district.
        
        Args:
            state_id (int): ID of state to update (optional)
            district_id (int): ID of district to update (optional)
        
        Returns:
            dict: Updated counts for state and district
        """
        result = {'state_updated': False, 'district_updated': False}
        
        if state_id:
            try:
                state = State.objects.get(id=state_id)
                count = Volunteer.objects.filter(
                    state_id=state_id, 
                    deleted_at__isnull=True
                ).count()
                state.volunteer_count = count
                state.save(update_fields=['volunteer_count', 'updated_at'])
                result['state_updated'] = True
                result['state_count'] = count
            except State.DoesNotExist:
                pass
        
        if district_id:
            try:
                district = District.objects.get(id=district_id)
                count = Volunteer.objects.filter(
                    district_id=district_id, 
                    deleted_at__isnull=True
                ).count()
                district.volunteer_count = count
                district.save(update_fields=['volunteer_count', 'updated_at'])
                result['district_updated'] = True
                result['district_count'] = count
            except District.DoesNotExist:
                pass
        
        return result
    
    @staticmethod
    def bulk_update_volunteer_counts():
        """
        Perform bulk update of all volunteer counts for states and districts.
        Use this after bulk import operations.
        
        Returns:
            dict: Summary of updates
        """
        states_updated = 0
        districts_updated = 0
        
        # Update all states
        states = State.objects.all()
        for state in states:
            count = Volunteer.objects.filter(
                state_id=state.id, 
                deleted_at__isnull=True
            ).count()
            if state.volunteer_count != count:
                state.volunteer_count = count
                state.save(update_fields=['volunteer_count', 'updated_at'])
                states_updated += 1
        
        # Update all districts
        districts = District.objects.all()
        for district in districts:
            count = Volunteer.objects.filter(
                district_id=district.id, 
                deleted_at__isnull=True
            ).count()
            if district.volunteer_count != count:
                district.volunteer_count = count
                district.save(update_fields=['volunteer_count', 'updated_at'])
                districts_updated += 1
        
        return {
            'states_updated': states_updated,
            'districts_updated': districts_updated,
            'total_updates': states_updated + districts_updated
        }
    
    @staticmethod
    def get_volunteer_statistics():
        """
        Get comprehensive volunteer statistics by state and district.
        
        Returns:
            dict: Statistics including top states/districts and totals
        """
        total_volunteers = Volunteer.objects.filter(
            deleted_at__isnull=True
        ).count()
        
        states_with_counts = State.objects.filter(
            volunteer_count__gt=0
        ).order_by('-volunteer_count')[:10]
        
        districts_with_counts = District.objects.filter(
            volunteer_count__gt=0
        ).order_by('-volunteer_count')[:10]
        
        return {
            'total_volunteers': total_volunteers,
            'total_states_with_volunteers': State.objects.filter(
                volunteer_count__gt=0
            ).count(),
            'total_districts_with_volunteers': District.objects.filter(
                volunteer_count__gt=0
            ).count(),
            'top_states': [
                {
                    'name': s.name,
                    'volunteer_count': s.volunteer_count
                } for s in states_with_counts
            ],
            'top_districts': [
                {
                    'name': d.name,
                    'state': d.state.name,
                    'volunteer_count': d.volunteer_count
                } for d in districts_with_counts
            ]
        }
