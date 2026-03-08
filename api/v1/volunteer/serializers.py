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

    organization_name = serializers.CharField(write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    blood_group = serializers.CharField(write_only=True, required=False)
    salutation = serializers.CharField(write_only=True, required=False)
    maritalstatus = serializers.CharField(write_only=True, required=False)
    education = serializers.CharField(write_only=True, required=False)
    skill = serializers.CharField(write_only=True, required=False)
    area_type = serializers.CharField(write_only=True, required=False)
    state_name = serializers.CharField(write_only=True, required=False)
    district_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Volunteer
        fields = "__all__"

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
        # Strip whitespace from all string fields (fixes Excel import issues)
        string_fields = ['aadhar', 'mobile', 'email', 'name', 'mybharat_id', 'emergency_contact']
        for field in string_fields:
            if field in attrs and isinstance(attrs[field], str):
                attrs[field] = attrs[field].strip()
        
        org_name = attrs.pop('organization_name', None)
        gender_label = attrs.pop('gender', None)
        blood_group_label = attrs.pop('blood_group', None)
        salutation_label = attrs.pop('salutation', None)
        maritalstatus_label = attrs.pop('maritalstatus', None)
        education_label = attrs.pop('education', None)
        skill_label = attrs.pop('skill', None)
        area_type_label = attrs.pop('area_type', None)
        state_name = attrs.pop('state_name', None)
        district_name = attrs.pop('district_name', None)

        if org_name and not attrs.get('organization'):
            org = Organization.objects.filter(name__iexact=org_name).first()
            if not org:
                raise serializers.ValidationError({'organization_name': 'Organization not found'})
            attrs['organization'] = org

        gender_id = attrs.get('gender_id')
        coerced_gender = gender_id if gender_id else self._coerce_gender(gender_label)
        if gender_label is not None and coerced_gender is None:
            raise serializers.ValidationError({'gender': 'Invalid gender'})
        if coerced_gender is not None:
            attrs['gender_id'] = coerced_gender

        blood_id = attrs.get('bloodgroup_id')
        coerced_bg = blood_id if blood_id else self._coerce_blood_group(blood_group_label)
        if blood_group_label is not None and coerced_bg is None:
            raise serializers.ValidationError({'blood_group': 'Invalid blood group'})
        if coerced_bg is not None:
            attrs['bloodgroup_id'] = coerced_bg

        salutation_id = attrs.get('salutation_id')
        coerced_sal = salutation_id if salutation_id else self._coerce_salutation(salutation_label)
        if salutation_label is not None and coerced_sal is None:
            raise serializers.ValidationError({'salutation': 'Invalid salutation'})
        if coerced_sal is not None:
            attrs['salutation_id'] = coerced_sal

        maritalstatus_id = attrs.get('maritalstatus_id')
        coerced_ms = maritalstatus_id if maritalstatus_id else self._coerce_maritalstatus(maritalstatus_label)
        if maritalstatus_label is not None and coerced_ms is None:
            raise serializers.ValidationError({'maritalstatus': 'Invalid marital status'})
        if coerced_ms is not None:
            attrs['maritalstatus_id'] = coerced_ms

        education_id = attrs.get('education_id')
        coerced_edu = education_id if education_id else self._coerce_education(education_label)
        if education_label is not None and coerced_edu is None:
            raise serializers.ValidationError({'education': 'Invalid education'})
        if coerced_edu is not None:
            attrs['education_id'] = coerced_edu

        skill_id = attrs.get('skill_id')
        coerced_skill = skill_id if skill_id else self._coerce_skill(skill_label)
        if skill_label is not None and coerced_skill is None:
            raise serializers.ValidationError({'skill': 'Invalid skill'})
        if coerced_skill is not None:
            attrs['skill_id'] = coerced_skill

        area_type_id = attrs.get('area_type_id')
        coerced_area = area_type_id if area_type_id else self._coerce_area_type(area_type_label)
        if area_type_label is not None and coerced_area is None:
            raise serializers.ValidationError({'area_type': 'Invalid area type'})
        if coerced_area is not None:
            attrs['area_type_id'] = coerced_area

        mis = attrs.get('mis_id')
        if mis is not None:
            attrs['mis_id'] = str(mis).strip()

        state_value = attrs.get('state')
        if isinstance(state_value, str):
            state_name = state_name or state_value
            attrs.pop('state', None)

        if state_name and not attrs.get('state'):
            state_obj = State.objects.filter(name__iexact=state_name.strip()).first()
            if not state_obj:
                state_obj = State.objects.create(name=state_name.strip())
            attrs['state'] = state_obj

        district_value = attrs.get('district')
        if isinstance(district_value, str):
            district_name = district_name or district_value
            attrs.pop('district', None)

        if district_name and not attrs.get('district'):
            qs = District.objects.all()
            if attrs.get('state'):
                qs = qs.filter(state=attrs['state'])
            district_obj = qs.filter(name__iexact=district_name.strip()).first()
            if not district_obj:
                # Auto-create district under resolved state if provided
                if attrs.get('state'):
                    district_obj = District.objects.create(name=district_name.strip(), state=attrs['state'])
                else:
                    raise serializers.ValidationError({'district': 'District not found'})
            attrs['district'] = district_obj

        return attrs