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


class VolunteerSerializer(serializers.ModelSerializer):

    organization_name = serializers.CharField(write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    blood_group = serializers.CharField(write_only=True, required=False)
    state_name = serializers.CharField(write_only=True, required=False)
    district_name = serializers.CharField(write_only=True, required=False)
    state_lgd_code = serializers.CharField(write_only=True, required=False)
    district_lgd_code = serializers.CharField(write_only=True, required=False)

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

    def validate(self, attrs):
        org_name = attrs.pop('organization_name', None)
        gender_label = attrs.pop('gender', None)
        blood_group_label = attrs.pop('blood_group', None)
        state_name = attrs.pop('state_name', None)
        district_name = attrs.pop('district_name', None)
        state_lgd_code = attrs.pop('state_lgd_code', None)
        district_lgd_code = attrs.pop('district_lgd_code', None)

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

        mis = attrs.get('mis_id')
        if mis is not None and not isinstance(mis, int):
            try:
                attrs['mis_id'] = int(mis)
            except (TypeError, ValueError):
                raise serializers.ValidationError({'mis_id': 'mis_id must be an integer'})

        state_value = attrs.get('state')
        if isinstance(state_value, str):
            state_name = state_name or state_value
            attrs.pop('state', None)

        if state_lgd_code and not attrs.get('state'):
            state_obj = State.objects.filter(lgd_code=str(state_lgd_code).strip()).first()
            if not state_obj:
                raise serializers.ValidationError({'state_lgd_code': 'State LGD code not found'})
            attrs['state'] = state_obj

        if state_name and not attrs.get('state'):
            state_obj = State.objects.filter(name__iexact=state_name.strip()).first()
            if not state_obj:
                state_obj = State.objects.create(name=state_name.strip())
            attrs['state'] = state_obj

        district_value = attrs.get('district')
        if isinstance(district_value, str):
            district_name = district_name or district_value
            attrs.pop('district', None)

        if district_lgd_code and not attrs.get('district'):
            district_obj = District.objects.filter(lgd_code=str(district_lgd_code).strip()).first()
            if not district_obj:
                raise serializers.ValidationError({'district_lgd_code': 'District LGD code not found'})
            if attrs.get('state') and district_obj.state_id != attrs['state'].id:
                raise serializers.ValidationError({'district_lgd_code': 'District does not belong to provided state'})
            attrs['district'] = district_obj

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