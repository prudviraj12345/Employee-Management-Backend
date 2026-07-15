from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

    def validate_department_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Department name is too short.")
        return value