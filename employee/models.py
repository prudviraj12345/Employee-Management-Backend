# from django.db import models
# from department.models import Department


# class Employee(models.Model):
#     employee_id = models.CharField(max_length=20, unique=True)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone = models.CharField(max_length=15)
#     department = models.ForeignKey(
#         Department,
#         on_delete=models.CASCADE,
#         related_name='employees'
#     )
#     designation = models.CharField(max_length=100)
#     salary = models.DecimalField(max_digits=10, decimal_places=2)
#     joining_date = models.DateField()
#     status = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.employee_id} - {self.first_name} {self.last_name}"
    

import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


from department.models import Department

# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------
class Employee(models.Model):
    class Designation(models.TextChoices):
        SOFTWARE_ENGINEER = "SE", "Software Engineer"
        SENIOR_ENGINEER = "SSE", "Senior Software Engineer"
        MANAGER = "MGR", "Manager"
        HR = "HR", "HR Executive"
        INTERN = "INT", "Intern"
        OTHER = "OTH", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # employee_id: business-facing ID, e.g. EMP001 — enforced at DB AND serializer level
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^EMP\d{3,6}$',
                message="employee_id must match the pattern EMP followed by 3-6 digits (e.g. EMP001)."
            )
        ],
    )

    full_name = models.CharField(max_length=150)

    # unique=True gives us a DB-level constraint; serializer adds a friendlier error message
    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{10,15}$',
                message="Phone number must be 10-15 digits, optionally starting with '+'."
            )
        ],
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,  # prevent deleting a department that still has employees
        related_name='employees',
    )

    designation = models.CharField(
        max_length=3,
        choices=Designation.choices,
        default=Designation.SOFTWARE_ENGINEER,
    )

    status = models.BooleanField(default=True)  # Active / Inactive
    joined_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['email']),
            models.Index(fields=['department', 'status']),
        ]

    def clean(self):
        """
        Model-level validation — runs on full_clean(), acts as a second safety
        net even if something bypasses the serializer (e.g. Django Admin, shell).
        """
        errors = {}

        if self.joined_date and self.joined_date > timezone.now().date():
            errors['joined_date'] = "Joined date cannot be in the future."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
