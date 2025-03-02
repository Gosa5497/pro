from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import (
    Department, Company, Student, Advisor, ChatGroup,
    DepartmentHead, Supervisor, Application,CompanyFeedback,
    Internship, FormTemplate,Task, Evaluation, Notification,CompanyAdmin,Role,UserRole,CustomField,CustomFieldValue
)
User = get_user_model()
 
class CompanyRegistrationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'industry', 'location', 'website', 'contact_email', 'contact_phone', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# Base Registration Form
class BaseRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=20)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'phone', 'password1', 'password2', 'profile_image'
        )

    def save(self, commit=True):
        # Save the user instance without committing to the database
        user = super().save(commit=False)
        
        # Handle profile image upload
        if 'profile_image' in self.files:  # Check if a file was uploaded
            user.profile_image = self.cleaned_data['profile_image']
        
        if commit:
            user.save()  # Save the user to the database
            self.save_m2m()  # Save many-to-many relationships (if any)
        
        return user

# Student Registration Form
class StudentRegistrationForm(BaseRegistrationForm):
    major = forms.CharField(max_length=100)
    year = forms.IntegerField(min_value=1, max_value=5)
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    resume = forms.FileField(required=False)

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ('major', 'year', 'department', 'resume')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True  # Set the user role
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                major=self.cleaned_data['major'],
                year=self.cleaned_data['year'],
                department=self.cleaned_data['department'],
                resume=self.cleaned_data['resume']
            )
        return user
class AdvisorRegistrationForm(BaseRegistrationForm):
    office_location = forms.CharField(max_length=255)
    department = forms.ModelChoiceField(queryset=Department.objects.all())

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ('office_location', 'department')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_advisor = True
        if commit:
            user.save()
            Advisor.objects.create(
                user=user,
                office_location=self.cleaned_data['office_location'],
                department=self.cleaned_data['department']
            )
        return user

# forms.py
class DepartmentHeadRegistrationForm(BaseRegistrationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    position = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'value': 'Department Head', 'readonly': 'readonly'})
    )

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ('position', 'department')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_department_head = True  # Set the user role
        if commit:
            user.save()
            # Create the DepartmentHead and associate it with the user
            DepartmentHead.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                position=self.cleaned_data['position']
            )
        return user
    
class DepartmentHeadUpdateForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_department_head=False),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    position = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'value': 'Department Head', 'readonly': 'readonly'})
    )

    class Meta:
        model = DepartmentHead
        fields = ['user', 'position']

class CompanyAdminRegistrationForm(BaseRegistrationForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all())
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company_admin = True
        if commit:
            user.save()
            company = self.cleaned_data['company']
            CompanyAdmin.objects.create(user=user, company=company)
        return user
class SupervisorRegistrationForm(BaseRegistrationForm):
    position = forms.CharField(max_length=100)
    company = forms.ModelChoiceField(queryset=Company.objects.all())

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ('position', 'company')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_supervisor = True
        if commit:
            user.save()  # Save the User instance
            Supervisor.objects.create(
                user=user,
                position=self.cleaned_data['position'],
                company=self.cleaned_data['company']
            )
        return user
class DepartmentRegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Department
        fields = ['name', 'description']

    def save(self, commit=True):
        department = super().save(commit=False)
        if commit:
            department.save()
        return department

# ------------------- Model Forms -------------------
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'industry', 'location', 'website', 
                 'contact_email', 'contact_phone', 'description']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['internship', 'description', 'deadline', 'status']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['internship', 'criteria', 'score', 'comments']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'message']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
        }
class CompanyAdminForm(forms.ModelForm):
    class Meta:
        model = CompanyAdmin
        fields = ['user', 'company', 'can_assign_supervisor', 'can_manage_applications', 'can_manage_internships']
# ------------------- Profile Update Forms -------------------
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['major', 'year', 'department', 'resume', 'status']

class AdvisorProfileForm(forms.ModelForm):
    class Meta:
        model = Advisor
        fields = ['department', 'office_location']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image']


class FullCRUDForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'

# User Forms

class UserForm(UserCreationForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Assign the selected role to the user
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)
        return user
# Department Forms
class DepartmentForm(FullCRUDForm):
    class Meta:
        model = Department
        fields = '__all__'

# Company Forms
class CompanyForm(FullCRUDForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

# Student Forms
class StudentForm(FullCRUDForm):
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {'resume': forms.FileInput(attrs={'class': 'form-control-file'})}

# Application Forms
class ApplicationForm(FullCRUDForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'date_applied': forms.DateInput(attrs={'type': 'date'}),
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }

# Advisor Form
class AdvisorForm(FullCRUDForm):
    class Meta:
        model = Advisor
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

# DepartmentHead Form
class DepartmentHeadForm(FullCRUDForm):
    class Meta:
        model = DepartmentHead
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

# Supervisor Form
class SupervisorForm(FullCRUDForm):
    class Meta:
        model = Supervisor
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }

# Internship Form
class InternshipForm(FullCRUDForm):
    class Meta:
        model = Internship
        fields = '__all__'
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
            'advisor': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Task Form
class TaskForm(FullCRUDForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'internship': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Evaluation Form
class EvaluationForm(FullCRUDForm):
    class Meta:
        model = Evaluation
        fields = '__all__'
        widgets = {
            'internship': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'criteria': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

# Notification Form
class NotificationForm(FullCRUDForm):
    class Meta:
        model = Notification
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'rows': 3}),
            'link': forms.URLInput(),
        }

# CompanyAdmin Form
class CompanyAdminForm(FullCRUDForm):
    class Meta:
        model = CompanyAdmin
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }

class CompanyFeedbackForm(forms.ModelForm):
    class Meta:
        model = CompanyFeedback
        fields = ['company', 'feedback']
# Role Form
class RoleForm(FullCRUDForm):
    class Meta:
        model = Role
        fields = '__all__'
        widgets = {
            'permissions': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

# UserRole Form
class UserRoleForm(FullCRUDForm):
    class Meta:
        model = UserRole
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

# CustomField Form
class CustomFieldForm(FullCRUDForm):
    class Meta:
        model = CustomField
        fields = '__all__'
        widgets = {
            'entity_type': forms.Select(attrs={'class': 'form-select'}),
            'field_type': forms.Select(attrs={'class': 'form-select'}),
        }

# CustomFieldValue Form
class CustomFieldValueForm(FullCRUDForm):
    class Meta:
        model = CustomFieldValue
        fields = '__all__'
        widgets = {
            'field': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.Textarea(attrs={'rows': 3}),
        }

# forms.py


class UserCreationWithRoleForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ('department_head', 'Department Head'),
            ('advisor', 'Advisor'),
            ('student', 'Student'),
            ('supervisor', 'Supervisor'),
            ('company_admin', 'Company Admin'),
        ],
        widget=forms.HiddenInput()  # Hide the role field in the form
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']
        if role == 'department_head':
            user.is_department_head = True
        elif role == 'advisor':
            user.is_advisor = True
        elif role == 'student':
            user.is_student = True
        elif role == 'supervisor':
            user.is_supervisor = True
        elif role == 'company_admin':
            user.is_company_admin = True
        if commit:
            user.save()
        return user

class FormGeneratorForm(forms.Form):
    form_type = forms.ChoiceField(choices=FormTemplate.FORM_TYPES, label="Select Form Type")
    duration = forms.CharField(max_length=50, label="Duration (e.g., Monthly, Weekly)")
    fields = forms.CharField(widget=forms.Textarea, label="Enter Fields (comma-separated)")
    description = forms.CharField(widget=forms.Textarea, label="Form Description")
# Complete all other forms following the same pattern...

class ChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = '__all__'
        widgets = {
            'participants': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class MonthlyPerformanceEvaluationForm(forms.Form):
    month = forms.CharField(label="Month", max_length=100)
    company_name = forms.CharField(label="Company Name", max_length=100)
    supervisor_name = forms.CharField(label="Supervisor's Name", max_length=100)
    supervisor_phone = forms.CharField(label="Supervisor's Phone No.", max_length=15)
    student_name = forms.CharField(label="Student's Full Name", max_length=100)
    student_id = forms.CharField(label="Student's ID No.", max_length=20)
    student_department = forms.CharField(label="Student's Department", max_length=100)

    # General Performance (25%)
    punctuality = forms.IntegerField(label="Punctuality (5%)", min_value=0, max_value=5)
    reliability = forms.IntegerField(label="Reliability (5%)", min_value=0, max_value=5)
    independence = forms.IntegerField(label="Independence In Work (5%)", min_value=0, max_value=5)
    communication = forms.IntegerField(label="Communication Skills (5%)", min_value=0, max_value=5)
    professionalism = forms.IntegerField(label="Professionalism (5%)", min_value=0, max_value=5)

    # Personal Skill (25%)
    speed_of_work = forms.IntegerField(label="Speed of Work (5%)", min_value=0, max_value=5)
    accuracy = forms.IntegerField(label="Accuracy (5%)", min_value=0, max_value=5)
    engagement = forms.IntegerField(label="Engagement (5%)", min_value=0, max_value=5)
    need_for_work = forms.IntegerField(label="Do you need him for your work (5%)", min_value=0, max_value=5)
    cooperation = forms.IntegerField(label="Cooperation with colleagues (5%)", min_value=0, max_value=5)

    # Professional Skills (50%)
    technical_skills = forms.IntegerField(label="Technical Skills (5%)", min_value=0, max_value=5)
    organizational_skills = forms.IntegerField(label="Organizational Skills (5%)", min_value=0, max_value=5)
    project_support = forms.IntegerField(label="Support of the project tasks (5%)", min_value=0, max_value=5)
    responsibility = forms.IntegerField(label="Responsibility in the task fulfillment (15%)", min_value=0, max_value=15)
    team_quality = forms.IntegerField(label="Quality as a team member (20%)", min_value=0, max_value=20)

    additional_comments = forms.CharField(label="Additional Comments", widget=forms.Textarea, required=False)
    

class InternshipLogbookForm(forms.Form):
    student_name = forms.CharField(label="Student’s Name", max_length=100)
    company_name = forms.CharField(label="Name of Company", max_length=100)
    supervisor_name = forms.CharField(label="Name of Supervisor", max_length=100)
    safety_guidelines = forms.ChoiceField(
        label="Have you been given a brief on the company safety guidelines?",
        choices=[("Yes", "Yes"), ("No", "No")],
        widget=forms.RadioSelect,
    )

    # Weekly Log Entries
    week_1_day_1_date = forms.DateField(label="Week 1, Day 1 - Date")
    week_1_day_1_work = forms.CharField(label="Week 1, Day 1 - Work Performed", widget=forms.Textarea)
    week_1_day_1_comment = forms.CharField(label="Week 1, Day 1 - Supervisor’s Comment", widget=forms.Textarea)

    week_1_day_2_date = forms.DateField(label="Week 1, Day 2 - Date")
    week_1_day_2_work = forms.CharField(label="Week 1, Day 2 - Work Performed", widget=forms.Textarea)
    week_1_day_2_comment = forms.CharField(label="Week 1, Day 2 - Supervisor’s Comment", widget=forms.Textarea)

    # Add more fields for other days and weeks as needed...