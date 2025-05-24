from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import *

#***************Registration Forms********************

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
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Gender")
    class Meta:
        model = User
        fields = (
            'username', 'gender', 'email', 'first_name', 'last_name', 
            'phone', 'password1', 'password2', 'profile_image'
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        # Handle profile image upload
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']

        if commit:
            user.save()
            self.save_m2m()

        return user

class SuperadminStudentForm(BaseRegistrationForm):
    student_id = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9/]+$',
                message='Student ID must contain only letters, numbers, and forward slashes (/).'
            )
        ],
        help_text="Example: ETS/0558/13"
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True
    )
    major = forms.CharField(max_length=100)
    year = forms.IntegerField()
    resume = forms.FileField(required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                department=self.cleaned_data['department'],
                major=self.cleaned_data['major'],
                year=self.cleaned_data['year'],
                resume=self.cleaned_data['resume']
            )
        return user
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True
    )
    major = forms.CharField(max_length=100)
    year = forms.IntegerField()
    # resume = forms.FileField(required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        # ✅ Corrected to use password1 (UserCreationForm default)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            Student.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                major=self.cleaned_data['major'],
                year=self.cleaned_data['year'],
                resume=self.cleaned_data['resume']
            )
        return user


class DepartmentHeadStudentForm(BaseRegistrationForm):
    major = forms.CharField(max_length=100)
    year = forms.IntegerField()
    resume = forms.FileField(required=False)  # Make resume optional

    def __init__(self, *args, **kwargs):
        self.department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if self.department:
            self.fields['department'] = forms.CharField(
                initial=self.department.name,
                disabled=True,
                help_text="Student will be automatically assigned to your department"
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            # Safely get resume, or None if not provided
            resume_file = self.cleaned_data.get('resume', None)
            Student.objects.create(
                user=user,
                department=self.department,
                major=self.cleaned_data['major'],
                year=self.cleaned_data['year'],
                resume=resume_file  # assign None if not uploaded
            )
        return user

class SuperadminAdvisorForm(BaseRegistrationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    office_location = forms.CharField(max_length=255)

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


class DepartmentHeadAdvisorForm(BaseRegistrationForm):
    office_location = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        self.department = kwargs.pop('department', None)
        super().__init__(*args, **kwargs)
        if self.department:
            self.fields['department'] = forms.CharField(
                initial=self.department.name,
                disabled=True,
                help_text="Advisor will be assigned to your department"
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_advisor = True
        if commit:
            user.save()
            Advisor.objects.create(
                user=user,
                office_location=self.cleaned_data['office_location'],
                department=self.department
            )
        return user
class DepartmentHeadRegistrationForm(BaseRegistrationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),  # default empty; will set in __init__
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only departments with no assigned DepartmentHead
        assigned_departments = DepartmentHead.objects.values_list('department_id', flat=True)
        self.fields['department'].queryset = Department.objects.exclude(id__in=assigned_departments)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_department_head = True
        if commit:
            user.save()
            DepartmentHead.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                position=self.cleaned_data['position']
            )
        return user

class CompanyAdminRegistrationForm(BaseRegistrationForm):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company']

    def __init__(self, *args, **kwargs):  # <-- FIXED: double underscores
        super().__init__(*args, **kwargs)
        assigned_companies = CompanyAdmin.objects.values_list('company_id', flat=True)
        self.fields['company'].queryset = Company.objects.exclude(id__in=assigned_companies)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company_admin = True
        if commit:
            user.save()
            company = self.cleaned_data['company']
            CompanyAdmin.objects.create(user=user, company=company)
        return user

class SuperadminSupervisorForm(BaseRegistrationForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)
    position = forms.CharField(max_length=100)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_supervisor = True
        if commit:
            user.save()
            Supervisor.objects.create(
                user=user,
                position=self.cleaned_data['position'],
                company=self.cleaned_data['company']
            )
        return user


class CompanyAdminSupervisorForm(BaseRegistrationForm):
    position = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        self.company_admin = kwargs.pop('company_admin', None)
        super().__init__(*args, **kwargs)
        if self.company_admin:
            self.fields['company'] = forms.CharField(
                initial=self.company_admin.company.name,
                disabled=True,
                help_text="Supervisor will be assigned to your company"
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_supervisor = True
        if commit:
            user.save()
            Supervisor.objects.create(
                user=user,
                position=self.cleaned_data['position'],
                company=self.company_admin.company
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

#=========================update form =========================
User = get_user_model()

from django.contrib.auth.hashers import make_password

class BaseUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=20)

    # Add password field for updating password
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text="Leave blank if you don't want to change the password."
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        # Only change password if it's provided
        if password:
            user.password = make_password(password)

        if commit:
            user.save()
        return user

class SuperadminStudentUpdateForm(BaseUpdateForm):
    major = forms.CharField(max_length=100)
    year = forms.IntegerField()
    resume = forms.FileField(required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'student'):
            self.fields['major'].initial = self.instance.student.major
            self.fields['year'].initial = self.instance.student.year
            self.fields['resume'].initial = self.instance.student.resume
            self.fields['department'].initial = self.instance.student.department

    def save(self, commit=True):
        user = super().save(commit)
        student = getattr(user, 'student', None)
        if student:
            student.major = self.cleaned_data['major']
            student.year = self.cleaned_data['year']
            student.resume = self.cleaned_data.get('resume', student.resume)
            student.department = self.cleaned_data['department']
            student.save()
        return user
class SuperadminAdvisorUpdateForm(BaseUpdateForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    office_location = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'advisor'):
            self.fields['department'].initial = self.instance.advisor.department
            self.fields['office_location'].initial = self.instance.advisor.office_location

    def save(self, commit=True):
        user = super().save(commit)
        advisor = getattr(user, 'advisor', None)
        if advisor:
            advisor.department = self.cleaned_data['department']
            advisor.office_location = self.cleaned_data['office_location']
            advisor.save()
        return user
class SuperadminSupervisorUpdateForm(BaseUpdateForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)
    position = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'supervisor'):
            self.fields['company'].initial = self.instance.supervisor.company
            self.fields['position'].initial = self.instance.supervisor.position

    def save(self, commit=True):
        user = super().save(commit)
        supervisor = getattr(user, 'supervisor', None)
        if supervisor:
            supervisor.company = self.cleaned_data['company']
            supervisor.position = self.cleaned_data['position']
            supervisor.save()
        return user
class DepartmentHeadUpdateForm(BaseUpdateForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    position = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta(BaseUpdateForm.Meta):
        # Include all base fields + department and position
        fields = BaseUpdateForm.Meta.fields + ['department', 'position']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assigned_departments = DepartmentHead.objects.exclude(user=self.instance).values_list('department_id', flat=True)
        self.fields['department'].queryset = Department.objects.exclude(id__in=assigned_departments)

        if hasattr(self.instance, 'departmenthead'):
            self.fields['department'].initial = self.instance.departmenthead.department
            self.fields['position'].initial = self.instance.departmenthead.position

    def save(self, commit=True):
        user = super().save(commit)
        department_head = getattr(user, 'departmenthead', None)
        if department_head:
            department_head.department = self.cleaned_data['department']
            department_head.position = self.cleaned_data['position']
            department_head.save()
        return user
class CompanyAdminUpdateForm(BaseUpdateForm):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude companies assigned to other company admins except this user's company
        assigned_companies = CompanyAdmin.objects.exclude(user=self.instance).values_list('company_id', flat=True)
        self.fields['company'].queryset = Company.objects.exclude(id__in=assigned_companies)

        if hasattr(self.instance, 'companyadmin'):
            self.fields['company'].initial = self.instance.companyadmin.company

    def save(self, commit=True):
        user = super().save(commit)
        company_admin = getattr(user, 'companyadmin', None)
        if company_admin:
            company_admin.company = self.cleaned_data['company']
            company_admin.save()
        return user
#**********Update Forms************=========

#**********CRUD Forms************ 
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields ='__all__'
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
class CompanyAdminForm(forms.ModelForm):
    class Meta:
        model = CompanyAdmin
        fields = ['user', 'company', 'can_assign_supervisor', 'can_manage_applications', 'can_manage_internships']
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['major', 'year', 'department', 'resume', 'status']

class AdvisorProfileForm(forms.ModelForm):
    class Meta:
        model = Advisor
        fields = ['department', 'office_location']

class FullCRUDForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'
# forms.py
class UserCreateForm(UserCreationForm):
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
            role = self.cleaned_data['role']
            UserRole.objects.create(user=user, role=role)
        return user

class CompanyForm(FullCRUDForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

# Student Forms
class StudentForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, disabled=False)
    last_name = forms.CharField(max_length=30, disabled=False)
    major = forms.CharField(max_length=100)
    email = forms.EmailField(disabled=False)
    phone = forms.CharField(max_length=20)
    profile_image = forms.ImageField(required=False)
    assign_advisor = forms.ModelChoiceField(
        queryset=Advisor.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Student
        fields = ['phone', 'profile_image', 'resume', 'assign_advisor']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['major'].initial = self.instance.major
            self.fields['profile_image'].initial = self.instance.user.profile_image

            # Enable assign_advisor only if the student has an approved application
            if self.instance.application_set.filter(status='Approved').exists():
                self.fields['assign_advisor'].queryset = Advisor.objects.filter(
                    department=self.instance.department
                )
            else:
                self.fields['assign_advisor'].disabled = True



def make_field_name(prefix, text, index):
    # Keep it simple and unique using index
    return f"{prefix}_qual_{index}"

# Define make_field_name to accept 3 arguments
def make_field_name(prefix, text, index):
    """Generate a sanitized field name using prefix, text, and index."""
    sanitized_text = text.lower().replace(' ', '_').replace('-', '_')
    return f"{prefix}_{sanitized_text}_{index}"

class ApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        required=True,
        label="Resume/CV",
        help_text="Upload your latest Resume or CV (PDF, DOC, DOCX format)."
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': 'Explain why you are a good fit for this internship...'
        }),
        label='Cover Letter',
        help_text='Highlight relevant skills and experience (max 500 words approx).',
        required=False
    )

    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']

    def __init__(self, *args, **kwargs):
        self.internship = kwargs.pop('internship', None)
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        self.dynamic_fields = {}

        if self.internship:
            # Required qualifications
            required_quals = self.internship.required_qualifications or ''
            if isinstance(required_quals, str):
                required_quals_iterable = [q.strip() for q in required_quals.split(',') if q.strip()]
            elif isinstance(required_quals, list):
                required_quals_iterable = [q.strip() for q in required_quals if isinstance(q, str) and q.strip()]
            else:
                required_quals_iterable = []

            for i, req_text in enumerate(required_quals_iterable):
                field_name = make_field_name('req', req_text, i)
                self.fields[field_name] = forms.CharField(
                    label=req_text,
                    required=True,
                    widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
                    help_text="Please provide details or confirmation regarding this requirement."
                )
                self.dynamic_fields[field_name] = req_text

            # Optional qualifications
            optional_quals = self.internship.optional_qualifications or ''
            if isinstance(optional_quals, str):
                optional_quals_iterable = [q.strip() for q in optional_quals.split(',') if q.strip()]
            elif isinstance(optional_quals, list):
                optional_quals_iterable = [q.strip() for q in optional_quals if isinstance(q, str) and q.strip()]
            else:
                optional_quals_iterable = []

            for i, opt_text in enumerate(optional_quals_iterable):
                field_name = make_field_name('opt', opt_text, i)
                self.fields[field_name] = forms.CharField(
                    label=f"{opt_text} (Optional)",
                    required=False,
                    widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
                    help_text="Provide details if applicable."
                )
                self.dynamic_fields[field_name] = opt_text

        # Add Bootstrap classes
        self.fields['resume'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['cover_letter'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        application = super().save(commit=False)
        responses = {}

        for field_name, original_text in self.dynamic_fields.items():
            if field_name in self.cleaned_data:
                responses[original_text] = self.cleaned_data[field_name]

        application.requirement_responses = responses

        if self.internship:
            application.internship = self.internship
        if self.student:
            application.student = self.student

        if commit:
            application.save()

        return application

       
class AdvisorForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = Advisor
        fields = ['office_location']  # Only allow changing office_location

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['profile_image'].initial = self.instance.user.profile_image

    def save(self, commit=True):
        advisor = super().save(commit=False)
        user = advisor.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.profile_image = self.cleaned_data['profile_image']

        if commit:
            user.save()
            advisor.save()
        return advisor

class DepartmentHeadAdvisorUpdateForm(BaseUpdateForm):
    office_location = forms.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        self.department = kwargs.pop('department', None)  # passed from the view
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'advisor'):
            self.fields['office_location'].initial = self.instance.advisor.office_location

    def save(self, commit=True):
        user = super().save(commit)
        advisor = getattr(user, 'advisor', None)
        if advisor:
            advisor.office_location = self.cleaned_data['office_location']
            if self.department:
                advisor.department = self.department
            advisor.save()
        return user

class DepartmentHeadForm(FullCRUDForm):
    class Meta:
        model = DepartmentHead
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

class SupervisorForm(FullCRUDForm):
    class Meta:
        model = Supervisor
        fields = ['position']  # Only include editable fields
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Add read-only fields for display only
            self.fields['user_info'] = forms.CharField(
                initial=self.instance.user.get_full_name(),
                label="User",
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.fields['company_info'] = forms.CharField(
                initial=self.instance.company.name,
                label="Company",
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
class AssignSupervisorForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.none(),
        label="Select Student",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    supervisor = forms.ModelChoiceField(
        queryset=Supervisor.objects.none(),
        label="Select Supervisor",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            # ✅ Filter students without an assigned supervisor
            self.fields['student'].queryset = Student.objects.filter(
                application__internship__company=company,
                application__status='Approved',
                assigned_supervisor__isnull=True
            ).distinct()

            self.fields['supervisor'].queryset = Supervisor.objects.filter(company=company)

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['company', 'title', 'description', 'duration', 'training_format', 
                  'training_types', 'required_qualifications', 'optional_qualifications']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Extract company_admin from kwargs
        self.company_admin = kwargs.pop('company_admin', None)
        super().__init__(*args, **kwargs)
        
        if self.company_admin:
            # Set the initial value for the company field
            self.fields['company'].initial = self.company_admin.company
            self.fields['company'].disabled = True  # Disable editing the company field

    def save(self, commit=True):
        # Ensure the company is set correctly when saving
        internship = super().save(commit=False)
        if self.company_admin:
            internship.company = self.company_admin.company
        if commit:
            internship.save()
        return internship

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

class AssignAdvisorForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['assigned_advisor']
        widgets = {
            'assigned_advisor': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            # Filter advisors by the student's department
            self.fields['assigned_advisor'].queryset = Advisor.objects.filter(
                department=self.instance.department
            )
class FormGeneratorForm(forms.Form):
    form_type = forms.ChoiceField(choices=FormTemplate.FORM_TYPES, label="Select Form Type")
    duration = forms.CharField(max_length=50, label="Duration (e.g., Monthly, Weekly)")
    fields = forms.CharField(widget=forms.Textarea, label="Enter Fields (comma-separated)")
    description = forms.CharField(widget=forms.Textarea, label="Form Description")

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
# **********Chat Group Forms************

class ChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name',]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DepartmentHeadChatGroupForm(ChatGroupForm):
    def __init__(self, *args, **kwargs):
        self.department_head = kwargs.pop('department_head')
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = f"{self.department_head.department.name} Discussions"

    def save(self, commit=True):
        group = super().save(commit=False)
        group.created_by = self.department_head.user
        group.created_by_role = 'department_head'
        group.department = self.department_head.department
        
        if commit:
            group.save()
            # Add all department students and head
            students = Student.objects.filter(department=group.department)
            group.participants.add(*[s.user for s in students])
            group.participants.add(self.department_head.user)
        return group
class AdvisorChatGroupForm(ChatGroupForm):
    def __init__(self, *args, **kwargs):
        self.advisor = kwargs.pop('advisor')
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = f"{self.advisor.user.get_full_name()}'s Advisory Group"

    def save(self, commit=True):
        group = super().save(commit=False)
        group.created_by = self.advisor.user
        group.created_by_role = 'advisor'
        group.advisor = self.advisor
        
        if commit:
            group.save()
            # Add advisor's students
            students = Student.objects.filter(assigned_advisor=self.advisor)
            group.participants.add(*[s.user for s in students])
            group.participants.add(self.advisor.user)
        return group

class SupervisorChatGroupForm(ChatGroupForm):
    def __init__(self, *args, **kwargs):
        self.supervisor = kwargs.pop('supervisor')
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = f"{self.supervisor.user.get_full_name()}'s Team"

    def save(self, commit=True):
        group = super().save(commit=False)
        group.created_by = self.supervisor.user
        group.created_by_role = 'supervisor'
        group.supervisor = self.supervisor
        
        if commit:
            group.save()
            # Add supervisor's students
            students = Student.objects.filter(assigned_supervisor=self.supervisor)
            group.participants.add(*[s.user for s in students])
            group.participants.add(self.supervisor.user)
        return group

class StudentChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        if self.student is None:
            raise ValueError("The 'student' keyword argument is required.")

        super().__init__(*args, **kwargs)
    def save(self, commit=True):
        group = super().save(commit=False)
        group.created_by = self.student.user
        group.created_by_role = 'student'
        group.internship = self.student.internship
        
        if commit:
            group.save()
            # Add students with approved applications for the same internship
            students = Student.objects.filter(
                application__internship=group.internship,
                application__status='Approved'
            ).distinct()
            group.participants.add(*[s.user for s in students])

        return group
class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content', 'file']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*, video/*, .pdf, .doc, .docx'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '').strip()
        file = cleaned_data.get('file')

        if not content and not file:
            raise forms.ValidationError("Either a message or file is required.")

        return cleaned_data

    
# **********Monthly Evaluation ,feedback,and student work report Form************

class WeeklyFeedbackForm(forms.ModelForm):
    class Meta:
        model = WeeklyFeedback
        fields = '__all__'  # Explicitly list fields to include
        
    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        self.supervisor = kwargs.pop('supervisor', None)
        self.week_number = kwargs.pop('week_number', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.student
        instance.supervisor = self.supervisor
        instance.week_number = self.week_number
        
        if commit:
            instance.save()
        return instance
    
# forms.py
class MonthlyEvaluationForm(forms.ModelForm):
    CATEGORY_FIELDS = {
        'general': ['punctuality', 'reliability', 'independence', 'communication', 'professionalism'],
        'personal': ['speed_of_work', 'accuracy', 'engagement', 'need_for_work', 'cooperation'],
        'professional': ['technical_skills', 'organizational_skills', 'project_support', 'responsibility', 'team_quality']
    }

    class Meta:
        model = MonthlyEvaluation
        fields = '__all__'
        exclude = ['student', 'supervisor', 'month', 'total_score', 'created_at', 'updated_at']
        widgets = {
            'additional_comments': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter overall comments...'}),
        }
        help_texts = {
            'responsibility': 'Score out of 15 points',
            'team_quality': 'Score out of 20 points'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input_attributes()

    def add_input_attributes(self):
        for field in self.fields:
            if field != 'additional_comments':
                self.fields[field].widget.attrs.update({
                    'min': 0,
                    'class': 'score-input',
                    'data-category': self.get_field_category(field)
                })
                if field == 'responsibility':
                    self.fields[field].widget.attrs['max'] = 15
                elif field == 'team_quality':
                    self.fields[field].widget.attrs['max'] = 20  # Set max value to 20
                else:
                    self.fields[field].widget.attrs['max'] = 5

    def get_field_category(self, field_name):
        for category, fields in self.CATEGORY_FIELDS.items():
            if field_name in fields:
                return category
        return ''

    def clean(self):
        cleaned_data = super().clean()
        category_totals = self.calculate_category_totals(cleaned_data)

        errors = []
        for category, total in category_totals.items():
            limit = MonthlyEvaluation.CATEGORY_LIMITS[category]
            if total > limit:
                errors.append(f"{category.capitalize()} category exceeds maximum of {limit} points")

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def calculate_category_totals(self, data):
        return {
            category: sum(data.get(field, 0) for field in fields)
            for category, fields in self.CATEGORY_FIELDS.items()
        }
    
class FinalEvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = '__all__'
        widgets = {
            'knowledge': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'problem_solving': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'quality': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'punctuality': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'initiative': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'dedication': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'cooperation': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'discipline': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'responsibility': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'socialization': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'communication': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'decision_making': forms.NumberInput(attrs={
                'min': 1, 'max': 5,
                'class': 'form-control',
                'style': 'width: 100px;'
            }),
            'potential_comments': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Enter detailed comments about student potential...'
            }),
            'job_offer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        exclude = ['internship', 'supervisor', 'total_mark', 'overall_performance']

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation if needed
        for field in self.fields:
            if field not in ['potential_comments', 'job_offer']:
                value = cleaned_data.get(field)
                if value and (value < 1 or value > 5):
                    self.add_error(field, 'Score must be between 1 and 5')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            if field != 'job_offer':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
class FeedbackForm(forms.ModelForm):
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Feedback",
        help_text="Provide detailed feedback for the student."
    )

    class Meta:
        model = Task
        fields = ['supervisor_feedback']
class StudentTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
class SupervisorTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['supervisor_feedback', ]
        widgets = {
            'supervisor_feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide feedback on the task...'}),
        }
class DailyTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [ 'description',]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_work_date(self):
        work_date = self.cleaned_data.get('work_date')
        if work_date > now().date():
            raise forms.ValidationError("You cannot submit a task for a future date.")
        return work_date

class DailyWorkReportForm(forms.ModelForm):
    class Meta:
        model = DailyWorkReport
        fields = '__all__'
        widgets = {
            'tasks_completed': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe all tasks you completed today...'
            }),
            'challenges_faced': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Any difficulties or challenges you encountered...'
            }),
            'lessons_learned': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What new skills or knowledge did you gain today?'
            }),
            'hours_worked': forms.NumberInput(attrs={
                'min': 0.5,
                'max': 12,
                'step': 0.5
            })
        }
        labels = {
            'hours_worked': 'Hours Worked (0.5-12)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tasks_completed'].required = True
        self.fields['hours_worked'].required = True       
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [ 'description',]
        exclude = ['work_date'] 
        widgets = {
            'work_date': forms.DateInput(attrs={'type': 'date'}),  # Add a date picker
            'description': forms.Textarea(attrs={'rows': 4}),
        }
class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = ['workdays_per_week']
        labels = {
            'workdays_per_week': 'Required Weekly Submissions'
        }
        help_texts = {
            'workdays_per_week': 'Number of daily reports required each week'
        }
        widgets = {
            'workdays_per_week': forms.NumberInput(attrs={
                'min': 1,
                'max': 7,
                'class': 'form-control'
            })
        }

class TaskFeedbackForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['supervisor_feedback']
        widgets = {
            'supervisor_feedback': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter your feedback for this week...'
            })
        }
class AdvisorTaskFeedbackForm(forms.Form):
    advisor_feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter your advisor feedback for this week...'
        }),
        required=True,
        label="Advisor Feedback"
    )
class CompanyRatingForm(forms.ModelForm):
    class Meta:
        model = CompanyRating
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control',
                'placeholder': 'Enter rating (1-5)'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional comments...'
            }),
        }
        labels = {
            'rating': 'Company Rating',
            'comments': 'Additional Comments'
        }
        help_texts = {
            'rating': '1 (Poor) - 5 (Excellent)',
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5")
        return rating
class FinalEvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'knowledge', 'problem_solving', 'quality', 'punctuality',
            'initiative', 'dedication', 'cooperation', 'discipline',
            'responsibility', 'socialization', 'communication', 
            'decision_making', 'potential_comments', 'job_offer'
        ]
        widgets = {
            field: forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control rating-input'
            }) for field in [
                'knowledge', 'problem_solving', 'quality', 'punctuality',
                'initiative', 'dedication', 'cooperation', 'discipline',
                'responsibility', 'socialization', 'communication', 
                'decision_making'
            ]
        }
        widgets.update({
            'potential_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'job_offer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        })
