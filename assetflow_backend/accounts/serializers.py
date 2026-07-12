from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class EmployeeMiniSerializer(serializers.ModelSerializer):
    """Lightweight representation used when nested inside other resources."""
    initials = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = User
        fields = ['id', 'employee_id', 'first_name', 'last_name', 'email',
                  'designation', 'department', 'department_name', 'role', 'initials']


class EmployeeSerializer(serializers.ModelSerializer):
    initials = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            'id', 'employee_id', 'username', 'first_name', 'last_name', 'email',
            'role', 'department', 'department_name', 'designation', 'phone',
            'avatar', 'is_active_employee', 'date_joined_org', 'initials', 'date_joined',
        ]
        read_only_fields = ['id', 'employee_id', 'date_joined']


class SignupSerializer(serializers.ModelSerializer):
    """
    Public sign-up: creates an employee profile with the default EMPLOYEE
    role. Admin access must be granted afterwards by an org admin, matching
    the note shown on the AssetFlow login screen.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
                  'department', 'designation', 'phone']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data, role=User.Role.EMPLOYEE)
        user.set_password(password)
        user.save()
        return user


class ChangeRoleSerializer(serializers.Serializer):
    """Admin-only: promote/demote an employee's role."""
    role = serializers.ChoiceField(choices=User.Role.choices)
