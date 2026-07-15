# from rest_framework import serializers
# from .models import Employee

# class EmployeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employee
#         fields = '__all__'

import re
from datetime import date

from rest_framework import serializers
from .models import Employee
from department.models import Department



# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------
class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone',
            'department', 'department_name', 'designation', 'status',
            'joined_date', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    # -----------------------------------------------------------------
    # Field-level validation
    # -----------------------------------------------------------------
    def validate_employee_id(self, value):
        value = value.strip().upper()
        if not re.match(r'^EMP\d{3,6}$', value):
            raise serializers.ValidationError(
                "employee_id must look like EMP001 (EMP + 3-6 digits)."
            )

        qs = Employee.objects.filter(employee_id=value)
        if self.instance:  # exclude self during update
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f"Employee ID '{value}' already exists.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        # DRF's EmailField already checks format; add the friendly uniqueness message
        qs = Employee.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f"Email '{value}' is already registered.")
        return value

    def validate_phone(self, value):
        value = value.strip().replace(' ', '')
        if not re.match(r'^\+?\d{10,15}$', value):
            raise serializers.ValidationError(
                "Phone must be 10-15 digits, optionally starting with '+'."
            )
        qs = Employee.objects.filter(phone=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(f"Phone number '{value}' is already in use.")
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Full name is too short.")
        if any(ch.isdigit() for ch in value):
            raise serializers.ValidationError("Full name cannot contain digits.")
        return value

    def validate_joined_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Joined date cannot be in the future.")
        return value

    def validate_department(self, value):
        if value is None:
            raise serializers.ValidationError("Department is required.")
        return value

    # -----------------------------------------------------------------
    # Object-level validation (cross-field rules go here)
    # -----------------------------------------------------------------
    def validate(self, attrs):
        # Example cross-field rule: interns shouldn't be marked inactive on creation
        designation = attrs.get('designation', getattr(self.instance, 'designation', None))
        status = attrs.get('status', getattr(self.instance, 'status', True))

        if designation == Employee.Designation.INTERN and status is False and not self.instance:
            raise serializers.ValidationError(
                {"status": "New intern records cannot be created as inactive."}
            )
        return attrs

    # -----------------------------------------------------------------
    # Consistent success/error envelope, per Section 5.3 of the guide
    # -----------------------------------------------------------------
    def to_representation(self, instance):
        return super().to_representation(instance)


class EmployeeCreateResponseSerializer(serializers.Serializer):
    """
    Optional helper to wrap a successful create/update in the
    {status, message, data} contract both teams agreed on.
    """
    status = serializers.CharField(default="success")
    message = serializers.CharField()
    data = serializers.DictField()