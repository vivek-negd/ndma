from django.db import models


class SalutationChoice(models.Model):
    """Master table for Salutation choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_salutation_choice"
        verbose_name = "Salutation Choice"
        verbose_name_plural = "Salutation Choices"

    def __str__(self):
        return self.label


class GenderChoice(models.Model):
    """Master table for Gender choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_gender_choice"
        verbose_name = "Gender Choice"
        verbose_name_plural = "Gender Choices"

    def __str__(self):
        return self.label


class BloodGroupChoice(models.Model):
    """Master table for Blood Group choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_bloodgroup_choice"
        verbose_name = "Blood Group Choice"
        verbose_name_plural = "Blood Group Choices"

    def __str__(self):
        return self.label


class MaritalStatusChoice(models.Model):
    """Master table for Marital Status choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_maritalstatus_choice"
        verbose_name = "Marital Status Choice"
        verbose_name_plural = "Marital Status Choices"

    def __str__(self):
        return self.label


class EducationChoice(models.Model):
    """Master table for Education choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_education_choice"
        verbose_name = "Education Choice"
        verbose_name_plural = "Education Choices"

    def __str__(self):
        return self.label


class SkillChoice(models.Model):
    """Master table for Skill choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_skill_choice"
        verbose_name = "Skill Choice"
        verbose_name_plural = "Skill Choices"

    def __str__(self):
        return self.label


class AreaTypeChoice(models.Model):
    """Master table for Area Type choices"""
    code = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "models_area_type_choice"
        verbose_name = "Area Type Choice"
        verbose_name_plural = "Area Type Choices"

    def __str__(self):
        return self.label
