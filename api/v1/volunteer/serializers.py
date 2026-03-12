from rest_framework import serializers
from models.volunteer import Volunteer
from models.organization import Organization
from models.state import State
from models.district import District


GENDER_MAP = {
    'male': 1,
    'm': 1,
    'female': 2,
    'f': 2,
    'other': 3,
    'o': 3,
}


BLOOD_GROUP_MAP = {
    'a+': 1,
    'a-': 2,
    'b+': 3,
    'b-': 4,
    'o+': 5,
    'o-': 6,
    'ab+': 7,
    'ab-': 8,
}

SALUTATION_MAP = {
    'mr': 1,
    'mr.': 1,
    'mrs': 2,
    'mrs.': 2,
    'ms': 3,
    'ms.': 3,
    'dr': 4,
    'dr.': 4,
    'prof': 5,
    'prof.': 5,
}

MARITALSTATUS_MAP = {
    'single': 1,
    'married': 2,
    'divorced': 3,
    'widowed': 4,
    'separated': 5,
}

EDUCATION_MAP = {
    'below 10th': 1,
    '10th pass': 2,
    '12th pass': 3,
    'diploma': 4,
    'bachelor': 5,
    'master': 6,
    'phd': 7,
    'other': 8,
}

SKILL_MAP = {
    'first aid': 1,
    'disaster management': 2,
    'rescue operations': 3,
    'community care': 4,
    'training': 5,
    'other': 6,
}

AREA_TYPE_MAP = {
    'urban': 1,
    'rural': 2,
    'semi-urban': 3,
}


class VolunteerSerializer(serializers.ModelSerializer):

    organization_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    gender = serializers.CharField(write_only=True, required=False, allow_blank=True)
    blood_group = serializers.CharField(write_only=True, required=False, allow_blank=True)
    salutation = serializers.CharField(write_only=True, required=False, allow_blank=True)
    maritalstatus = serializers.CharField(write_only=True, required=False, allow_blank=True)
    education = serializers.CharField(write_only=True, required=False, allow_blank=True)
    skill = serializers.CharField(write_only=True, required=False, allow_blank=True)
    area_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    state_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    district_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Volunteer
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make ALL fields optional and allow blank
        for field_name, field in self.fields.items():
            field.required = False
            field.allow_blank = True
            field.allow_null = True

    def _coerce_gender(self, gender_value):
        if gender_value is None:
            return None
        if isinstance(gender_value, int):
            return gender_value
        key = str(gender_value).strip().lower()
        return GENDER_MAP.get(key)

    def _coerce_blood_group(self, bg_value):
        if bg_value is None:
            return None
        if isinstance(bg_value, int):
            return bg_value
        key = str(bg_value).strip().lower()
        return BLOOD_GROUP_MAP.get(key)

    def _coerce_salutation(self, sal_value):
        if sal_value is None:
            return None
        if isinstance(sal_value, int):
            return sal_value
        key = str(sal_value).strip().lower()
        return SALUTATION_MAP.get(key)

    def _coerce_maritalstatus(self, ms_value):
        if ms_value is None:
            return None
        if isinstance(ms_value, int):
            return ms_value
        key = str(ms_value).strip().lower()
        return MARITALSTATUS_MAP.get(key)

    def _coerce_education(self, edu_value):
        if edu_value is None:
            return None
        if isinstance(edu_value, int):
            return edu_value
        key = str(edu_value).strip().lower()
        return EDUCATION_MAP.get(key)

    def _coerce_skill(self, skill_value):
        if skill_value is None:
            return None
        if isinstance(skill_value, int):
            return skill_value
        key = str(skill_value).strip().lower()
        return SKILL_MAP.get(key)

    def _coerce_area_type(self, area_value):
        if area_value is None:
            return None
        if isinstance(area_value, int):
            return area_value
        key = str(area_value).strip().lower()
        return AREA_TYPE_MAP.get(key)

    def validate(self, attrs):
        """
        ZERO VALIDATION - Accept ALL data without any checks
        Just clean up the inputs and pass through
        """
        # Strip whitespace from string fields only
        string_fields = ['aadhar', 'mobile', 'email', 'name', 'mybharat_id', 'emergency_contact', 'postal_code', 'town', 'village', 'full_address']
        for field in string_fields:
            if field in attrs and isinstance(attrs[field], str):
                attrs[field] = attrs[field].strip()
        
        # Remove custom fields that won't be saved
        attrs.pop('organization_name', None)
        attrs.pop('gender', None)
        attrs.pop('blood_group', None)
        attrs.pop('salutation', None)
        attrs.pop('maritalstatus', None)
        attrs.pop('education', None)
        attrs.pop('skill', None)
        attrs.pop('area_type', None)
        attrs.pop('state_name', None)
        attrs.pop('district_name', None)
        
        # Convert empty strings to None for all fields to allow NULL saving
        for key in list(attrs.keys()):
            if attrs[key] == '':
                attrs[key] = None
        
        # That's it - ZERO validation, just accept the data
        return attrs