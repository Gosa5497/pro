from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *

# ------------------- User & Registration Serializers -------------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)

# ------------------- Role-Specific Registration Serializers -------------------
class StudentRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Student
        fields = ['user', 'major', 'year', 'department', 'resume', 'status']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_student'] = True
        user = User.objects.create_user(**user_data)
        return Student.objects.create(user=user, **validated_data)

class AdvisorRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Advisor
        fields = ['user', 'department', 'office_location']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_advisor'] = True
        user = User.objects.create_user(**user_data)
        return Advisor.objects.create(user=user, **validated_data)

class DepartmentHeadRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = DepartmentHead
        fields = ['user', 'department']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_department_head'] = True
        user = User.objects.create_user(**user_data)
        return DepartmentHead.objects.create(user=user, **validated_data)

class SupervisorRegistrationSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = Supervisor
        fields = ['user', 'company', 'position']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_supervisor'] = True
        user = User.objects.create_user(**user_data)
        return Supervisor.objects.create(user=user, **validated_data)

# ------------------- Model Serializers -------------------
class DepartmentHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentHead
        fields = '__all__'
        depth = 1

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
class CompanyAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())

    class Meta:
        model = CompanyAdmin
        fields = ['id', 'user', 'company', 'role', 'created_at']
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        depth = 1

class AdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advisor
        fields = '__all__'
        depth = 1

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = '__all__'
        depth = 1

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = '__all__'
        depth = 2

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyEvaluation
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'