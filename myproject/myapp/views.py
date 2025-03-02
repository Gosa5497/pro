from rest_framework import viewsets, generics
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import *
from django.http import JsonResponse
from django.db.models import Q
from .models import Feedback,CompanyFeedback,ChatMessage, PrivateMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
import openai
from .serializers import *
from .models import UserRole

from .forms import (
    DepartmentHeadRegistrationForm,MonthlyPerformanceEvaluationForm,InternshipLogbookForm, ChatGroupForm, FormTemplate,CompanyFeedbackForm,FormGeneratorForm,DepartmentForm,DepartmentHeadForm,DepartmentHeadUpdateForm,CustomFieldValueForm,CustomFieldForm,UserRoleForm,EvaluationForm,InternshipForm,TaskForm, StudentRegistrationForm,CompanyAdminRegistrationForm,
    AdvisorRegistrationForm,UserCreationWithRoleForm,NotificationForm,RoleForm,UserForm,CompanyRegistrationForm,CompanyAdminForm,ApplicationForm,StudentForm,AdvisorForm,CompanyForm, SupervisorRegistrationForm, DepartmentRegistrationForm
)
def home(request):
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'home.html')

@login_required
def communication_page(request):
    return render(request, 'departement_head/communication_page.html')
@login_required
def existing_internships(request):
    # Fetch all internships
    internships = Internship.objects.all()
    
    # Pass the internships to the template
    context = {
        'internships': internships,
    }
    return render(request, 'company/existing_internships.html', context)


@login_required
def accept_application(request, application_id):
    # Ensure only company admins can accept applications
    if not request.user.is_company_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('applicant_list', internship_id=application.internship.id)

    # Get the application
    application = get_object_or_404(Application, id=application_id)

    # Update the application status to "Approved"
    application.status = 'Approved'
    application.save()

    messages.success(request, f"Application {application_id} has been approved.")
    return redirect('applicant_list', internship_id=application.internship.id)

@login_required
def reject_application(request, application_id):
    # Ensure only company admins can reject applications
    if not request.user.is_company_admin:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('applicant_list', internship_id=application.internship.id)

    # Get the application
    application = get_object_or_404(Application, id=application_id)

    # Update the application status to "Rejected"
    application.status = 'Rejected'
    application.save()

    messages.success(request, f"Application {application_id} has been rejected.")
    return redirect('applicant_list', internship_id=application.internship.id)

def post_internship(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_admin_dashboard')
    else:
        form = InternshipForm()
    return render(request, 'company/post_internship.html', {'form': form})
def view_internships(request):
    internships = Internship.objects.filter(company=request.user.companyadmin.company)
    return render(request, 'company/view_internships.html', {'internships': internships})
def update_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    if request.method == "POST":
        # Handle form submission to update the internship
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            messages.success(request, 'Internship updated successfully!')
            return redirect('view_internships')
    else:
        form = InternshipForm(instance=internship)
    return render(request, 'company/update_intern.html', {'form': form})

def delete_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    if request.method == "POST":
        internship.delete()
        messages.success(request, 'Internship deleted successfully!')
    return redirect('view_internships')

def toggle_internship_status(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    internship.is_open = not internship.is_open  # Toggle the status
    internship.save()
    messages.success(request, f'Internship status updated to {"Open" if internship.is_open else "Closed"}.')
    return redirect('view_internships')

def apply_internship(request, internship_id):
    # Get the internship
    internship = get_object_or_404(Internship, id=internship_id)
    
    # Get the logged-in student
    student = get_object_or_404(Student, user=request.user)

    # Check if the internship is open
    if not internship.is_open:
        messages.error(request, 'This internship is closed and cannot be applied to.')
        return redirect('view_internships')

    # Check if the student has already applied
    if Application.objects.filter(student=student, internship=internship).exists():
        messages.warning(request, 'You have already applied for this internship.')
        return redirect('view_internships')

    # Create a new application
    Application.objects.create(
        student=student,
        internship=internship,
        status='Pending'  # Default status
    )
    messages.success(request, 'Your application has been submitted successfully!')
    return redirect('view_internships')

@login_required
def applicant_list(request, internship_id):
    # Get the internship by its ID
    internship = get_object_or_404(Internship, id=internship_id)

    # Fetch all applications for the specified internship
    applications = Application.objects.filter(internship=internship).select_related('student')

    # Prepare a list of applicants (name and email) for the template
    applicants = []
    for application in applications:
        student = application.student
        applicant_data = {
            'name': f"{student.user.first_name} {student.user.last_name}",  # Concatenate first and last name
            'email': student.user.email,
            'id': application.id  # Use 'id' instead of 'application_id'
        }
        applicants.append(applicant_data)

    context = {
        'internship': internship,
        'applicants': applicants,  # Pass the list of applicants to the template
    }

    return render(request, 'company/applicant_list.html', context)

@login_required
def apply_internship(request, internship_id):
    # Get the internship by its ID
    internship = get_object_or_404(Internship, id=internship_id)

    # Ensure only students can apply for internships
    if not hasattr(request.user, 'student'):
        messages.error(request, "Only students can apply for internships.")
        return redirect('existing_internships')

    student = request.user.student

    # Check if the student has already applied to this internship
    if Application.objects.filter(internship=internship, student=student).exists():
        messages.error(request, "You have already applied to this internship.")
        return redirect('existing_internships')

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship  # Assign the internship from the URL
            application.student = student  # Assign the logged-in student
            application.save()  # Save the application to the database
            messages.success(request, "Your application has been submitted!")
            return redirect('applicant_list', internship_id=internship.id)  # Redirect to the applicant list
        else:
            messages.error(request, "There was an error with your application. Please try again.")
    else:
        form = ApplicationForm()

    return render(request, 'students/apply_internship.html', {'internship': internship, 'form': form})
@login_required
def private_chat_list(request, role):
    """Displays a list of users the department head can chat with."""
    users = []
    if role == 'advisors' and hasattr(request.user, 'departmenthead'):
        users = Advisor.objects.filter(department=request.user.departmenthead.department)
    elif role == 'supervisors':
        users = Supervisor.objects.all()
    elif role == 'company_admins':
        users = CompanyAdmin.objects.all()

    return render(request, 'departement_head/private_chat_list.html', {
        'users': users,
        'role': role
    })

@login_required
def private_chat(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            try:
                PrivateMessage.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    message=message_content
                )
                messages.success(request, "Message sent successfully!")
            except Exception as e:
                messages.error(request, f"Failed to send message: {str(e)}")
        else:
            messages.warning(request, "Message cannot be empty!")
        return redirect('private_chat', user_id=user_id)

    # Get messages between users
    chat_messages = PrivateMessage.objects.filter(
        models.Q(sender=request.user, receiver=receiver) |
        models.Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')

    return render(request, 'departement_head/private_chat.html', {
        'receiver': receiver,
        'chat_messages': chat_messages  # Ensure this matches the template variable
    })


@login_required
def group_chat(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            try:
                GroupMessage.objects.create(
                    sender=request.user,
                    group=group,
                    message=message_content
                )
                messages.success(request, "Message sent successfully!")
            except Exception as e:
                messages.error(request, f"Failed to send message: {str(e)}")
        else:
            messages.warning(request, "Message cannot be empty!")
        return redirect('group_chat', group_id=group_id)

    # Get messages for the group
    group_messages = GroupMessage.objects.filter(group=group).order_by('timestamp')

    return render(request, 'departement_head/group_chat.html', {
        'group': group,
        'messages': group_messages
    })
@login_required
def group_chat_students(request):
    # Auto-create group for students on internships
    department = request.user.departmenthead.department
    students = Student.objects.filter(department=department, internship__isnull=False)
    
    group, created = ChatGroup.objects.get_or_create(
        name=f"{department.name} Internship Group",
        department=department,
        created_by=request.user,
        is_private=False
    )
    if created:
        group.participants.add(request.user)
        for student in students:
            group.participants.add(student.user)
    
    messages = GroupMessage.objects.filter(group=group).order_by('timestamp')
    return render(request, 'departement_head/group_chat.html', {
        'group': group,
        'messages': messages
    })
@login_required
def create_chat_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            form.save_m2m()  # Save many-to-many relationships (e.g., participants)
            return redirect('group_chat', group_id=group.id)
    else:
        form = ChatGroupForm()

    return render(request, 'departement_head/create_chat_group.html', {
        'form': form
    })
@login_required
def list_chat_groups(request):
    # Fetch chat groups where the current user is a participant
    chat_groups = ChatGroup.objects.filter(participants=request.user)
    
    return render(request, 'departement_head/list_chat_groups.html', {
        'chat_groups': chat_groups
    })
@login_required
def send_group_message(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            try:
                GroupMessage.objects.create(
                    sender=request.user,
                    group=group,
                    message=message_content
                )
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
def profile(request):
    return render(request, 'departement_head/profile.html')
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        user_profile = user  # This should directly refer to User since profile info is in User
        user_profile.phone = request.POST.get('phone')
        user_profile.bio = request.POST.get('bio')
        user_profile.address = request.POST.get('address')

        if 'profile_image' in request.FILES:
            user_profile.profile_image = request.FILES['profile_image']
            print("Profile image uploaded.")

        user_profile.save()  # Save the user object

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'departement_head/edit_profile.html')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class CRUDMixin(LoginRequiredMixin):
    model = None
    form_class = None
    success_url = reverse_lazy('home')
    template_name = 'crud_form.html'
# ---------------------------- USER CRUD VIEWS ----------------------------
class RoleSelectionView(TemplateView):
    template_name = 'role_selection.html'
def user_create(request):
    if request.method == 'POST':
        # Get the selected role from the POST data
        role = request.POST.get('role')
        form = UserCreationWithRoleForm(request.POST)
        if form.is_valid():
            # Save the user with the selected role
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('admin_dashboard')
        else:
            print("Form errors:", form.errors)  # Debugging: Print form errors
    else:
        # Get the selected role from the query parameters
        role = request.GET.get('role')
        form = UserCreationWithRoleForm(initial={'role': role})
    
    return render(request, 'user_create.html', {'form': form})
class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    View for creating a new user.
    Accessible only by superusers.
    """
    model = User
    form_class = UserForm
    template_name = 'form.html'  # Template for the form
    success_url = reverse_lazy('admin_dashboard')  # Redirect to admin dashboard after creation

    def test_func(self):
        """Ensure only superusers can create users."""
        return self.request.user.is_superuser

    def form_valid(self, form):
        """Set additional fields or perform actions before saving the user."""
        messages.success(self.request, 'User created successfully!')
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating an existing user.
    Accessible only by superusers.
    """
    model = User
    form_class = UserForm
    template_name = 'form.html'  # Template for the form
    success_url = reverse_lazy('admin_dashboard')  # Redirect to admin dashboard after update

    def test_func(self):
        """Ensure only superusers can update users."""
        return self.request.user.is_superuser

    def form_valid(self, form):
        """Set additional fields or perform actions before saving the user."""
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting an existing user.
    Accessible only by superusers.
    """
    model = User
    template_name = 'users/user_confirm_delete.html'  # Template for delete confirmation
    success_url = reverse_lazy('admin_dashboard')  # Redirect to admin dashboard after deletion

    def test_func(self):
        """Ensure only superusers can delete users."""
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        """Display a success message after deletion."""
        messages.success(self.request, 'User deleted successfully!')
        return super().delete(request, *args, **kwargs)
# UserRole CRUD
class UserRoleListView(CRUDMixin, ListView):
    model = UserRole
    template_name = 'user_role/list.html'
    context_object_name = 'user_roles'

class UserRoleCreateView(CreateView):
    model = UserRole
    form_class = UserRoleForm
    template_name = 'crud_form.html'  # Ensure this matches the template name
    success_url = reverse_lazy('admin_dashboard')

class UserRoleUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = UserRole
    form_class = UserRoleForm
    success_url = reverse_lazy('user_role_list')

class UserRoleDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = UserRole
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('user_role_list')
# CustomFieldValue CRUD
class CustomFieldValueListView(CRUDMixin, ListView):
    model = CustomFieldValue
    template_name = 'custom_field_value/list.html'
    context_object_name = 'custom_field_values'

class CustomFieldValueCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = CustomFieldValue
    form_class = CustomFieldValueForm
    success_url = reverse_lazy('custom_field_value_list')

class CustomFieldValueUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = CustomFieldValue
    form_class = CustomFieldValueForm
    success_url = reverse_lazy('custom_field_value_list')

class CustomFieldValueDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = CustomFieldValue
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('custom_field_value_list')
# CustomField CRUD
class CustomFieldListView(CRUDMixin, ListView):
    model = CustomField
    template_name = 'custom_field/list.html'
    context_object_name = 'custom_fields'

class CustomFieldCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = CustomField
    form_class = CustomFieldForm
    success_url = reverse_lazy('custom_field_list')

class CustomFieldUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = CustomField
    form_class = CustomFieldForm
    success_url = reverse_lazy('custom_field_list')

class CustomFieldDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = CustomField
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('custom_field_list')

# Department CRUD
class DepartmentListView(CRUDMixin, ListView):
    model = Department
    template_name = 'department/list.html'
    context_object_name = 'departments'
class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'department/department_form.html'
    success_url = reverse_lazy('admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully!')
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'department/department_form.html'
    success_url = reverse_lazy('admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully!')
        return super().form_valid(form)

class DepartmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Department
    template_name = 'departments/department_confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Department deleted successfully!')
        return super().delete(request, *args, **kwargs)


def department_head_create(request):
    if request.method == 'POST':
        form = DepartmentHeadRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form (this will create a new user and department head)
            form.save()
            messages.success(request, 'Department head registered successfully.')
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
        else:
            print("Form errors:", form.errors)  # Debugging: Print form errors
    else:
        form = DepartmentHeadRegistrationForm()
    
    return render(request, 'departement_head/department_head_create.html', {'form': form})

def department_head_update(request, department_id):
    department = get_object_or_404(Department, id=department_id)  # Get the department
    department_head = DepartmentHead.objects.filter(department=department).first()  # Get the current department head

    if request.method == 'POST':
        form = DepartmentHeadUpdateForm(request.POST, instance=department_head)
        if form.is_valid():
            # Save the form (this will update or create the department head)
            department_head = form.save(commit=False)
            department_head.department = department  # Associate with the department
            department_head.save()
            messages.success(request, 'Department head updated successfully.')
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
        else:
            print("Form errors:", form.errors)  # Debugging: Print form errors
    else:
        # Pre-fill the form with the current department head (if it exists)
        form = DepartmentHeadUpdateForm(instance=department_head)
    
    return render(request, 'departement_head/department_head_update.html', {'form': form, 'department': department})

# Student CRUD
class StudentListView(CRUDMixin, ListView):
    model = Student
    template_name = 'student/list.html'
    context_object_name = 'students'

class StudentCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    success_url = reverse_lazy('student_list')

class StudentUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    success_url = reverse_lazy('student_list')

class StudentDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Student
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('student_list')

# Advisor CRUD
def is_department_head(user):
    return user.is_authenticated and hasattr(user, 'is_department_head') and user.is_department_head
@login_required
@user_passes_test(is_department_head)
def advisor_management(request):
    department = request.user.departmenthead.department
    advisors = Advisor.objects.filter(department=department)
    return render(request, 'advisors/advisor_management.html', {
        'advisors': advisors,
        'departments': Department.objects.all()
    })

@login_required
@user_passes_test(is_department_head)
def advisor_register(request):
    if request.method == "POST":
        form = AdvisorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and related data
            login(request, user)
            messages.success(request, 'Advisor registered successfully!')
            return redirect('department_head_dashboard')
    else:
        form = AdvisorRegistrationForm()
    return render(request, 'advisors/advisor_register.html', {'form': form})
@login_required
@user_passes_test(is_department_head)
def view_advisor_details(request, advisor_user_id):
    advisor = get_object_or_404(Advisor, user_id=advisor_user_id)
    chat_messages = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=advisor.user) |
        Q(sender=advisor.user, receiver=request.user)
    ).order_by('timestamp')
    
    return render(request, 'advisors/view_advisor_details.html', {
        'advisor': advisor,
        'chat_messages': chat_messages
    })

@login_required
@user_passes_test(is_department_head)
def update_advisor(request, advisor_user_id):
    advisor = get_object_or_404(Advisor, user_id=advisor_user_id)
    if request.method == 'POST':
        form = AdvisorForm(request.POST, instance=Advisor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Advisor updated successfully!')
            return redirect('advisor_management')
    else:
        form = AdvisorForm(instance=Advisor)
    return render(request, 'advisors/view_advisor_details.html', {'form': form, 'company': Advisor})
@login_required
@user_passes_test(is_department_head)
def send_message(request, advisor_user_id):
    advisor = get_object_or_404(Advisor, user_id=advisor_user_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=advisor.user,
                content=message
            )
    return redirect('view_advisor_details', advisor_user_id=advisor_user_id)
@login_required
@user_passes_test(is_department_head)
def delete_advisor(request, advisor_id):
    advisor = get_object_or_404(Advisor, id=advisor_id)
    if request.method == 'POST':
        advisor.user.delete()
        messages.success(request, 'Advisor deleted successfully')
    return redirect('advisor_management')
class AdvisorListView(CRUDMixin, ListView):
    model = Advisor
    template_name = 'advisor/list.html'
    context_object_name = 'advisors'

class AdvisorCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Advisor
    form_class = AdvisorForm
    success_url = reverse_lazy('advisor_list')

class AdvisorUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Advisor
    form_class = AdvisorForm
    success_url = reverse_lazy('advisor_list')

class AdvisorDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Advisor
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('advisor_list')

# Application CRUD
class ApplicationListView(CRUDMixin, ListView):
    model = Application
    template_name = 'application/list.html'
    context_object_name = 'applications'

class ApplicationCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    success_url = reverse_lazy('application_list')

class ApplicationUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    success_url = reverse_lazy('application_list')

class ApplicationDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Application
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('application_list')
# Role CRUD
class RoleListView(CRUDMixin, ListView):
    model = Role
    template_name = 'role/list.html'
    context_object_name = 'roles'

class RoleCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    success_url = reverse_lazy('role_list')

class RoleUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    success_url = reverse_lazy('role_list')

class RoleDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Role
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('role_list')

# Internship CRUD
class InternshipListView(CRUDMixin, ListView):
    model = Internship
    template_name = 'internship/list.html'
    context_object_name = 'internships'

class InternshipCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Internship
    form_class = InternshipForm
    success_url = reverse_lazy('internship_list')

class InternshipUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Internship
    form_class = InternshipForm
    success_url = reverse_lazy('internship_list')

class InternshipDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Internship
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('internship_list')

# Task CRUD
class TaskListView(CRUDMixin, ListView):
    model = Task
    template_name = 'task/list.html'
    context_object_name = 'tasks'

class TaskCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')

class TaskUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('task_list')

class TaskDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Task
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('task_list')
# CompanyAdmin CRUD
class CompanyAdminListView(CRUDMixin, ListView):
    model = CompanyAdmin
    template_name = 'company_admin/list.html'
    context_object_name = 'company_admins'

class CompanyAdminCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = CompanyAdmin
    form_class = CompanyAdminForm
    success_url = reverse_lazy('company_admin_list')

class CompanyAdminUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = CompanyAdmin
    form_class = CompanyAdminForm
    success_url = reverse_lazy('company_admin_list')

class CompanyAdminDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = CompanyAdmin
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('company_admin_list')
#   CRUD FOR Notification

class NotificationListView(CRUDMixin, ListView):
    model = Evaluation
    template_name = 'notification/list.html'
    context_object_name = 'notification'

class NotificationCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Notification
    form_class = NotificationForm
    success_url = reverse_lazy('notificationForm_list')

class NotificationUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model =Notification
    form_class = NotificationForm
    success_url = reverse_lazy('notification_list')

class NotificationDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Notification
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('notification_list')
# Example for Evaluation
class EvaluationListView(CRUDMixin, ListView):
    model = Evaluation
    template_name = 'evaluation/list.html'
    context_object_name = 'evaluations'

class EvaluationCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = Evaluation
    form_class = EvaluationForm
    success_url = reverse_lazy('evaluation_list')

class EvaluationUpdateView(CRUDMixin, AdminRequiredMixin, UpdateView):
    model = Evaluation
    form_class = EvaluationForm
    success_url = reverse_lazy('evaluation_list')

class EvaluationDeleteView(CRUDMixin, AdminRequiredMixin, DeleteView):
    model = Evaluation
    template_name = 'delete_confirm.html'
    success_url = reverse_lazy('evaluation_list')

# Create similar classes for all other models...
@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')   # Redirect to Django admin dashboard
    if hasattr(request.user, 'is_company_admin') and request.user.is_company_admin:
        return redirect('company_admin_dashboard')
    if hasattr(request.user, 'is_student') and request.user.is_student:
        return redirect('student_dashboard')
    elif hasattr(request.user, 'is_department_head') and request.user.is_department_head:
        return redirect('department_head_dashboard')
    elif hasattr(request.user, 'is_supervisor') and request.user.is_supervisor:
        return redirect('supervisor_dashboard')
    elif hasattr(request.user, 'is_advisor') and request.user.is_advisor:
        return redirect('advisor_dashboard')

    return redirect('home')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Incorrect username or password")
    
    return redirect('home')  # Redirect back to home with error mess
def is_admin(user):
    return user.is_superuser
# Company Admin Registration View
def company_admin_register(request):
    if request.method == "POST":
        form = CompanyAdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Company Admin registered successfully!')
            return redirect('company_admin_dashboard')
    else:
        form = CompanyAdminRegistrationForm()
    return render(request, 'Company_Admin/company_admin_register.html', {'form': form})

# Company Admin Dashboard
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def company_admin_dashboard(request):
    company = request.user.companyadmin.company  # Get the admin's company
    
    stats = {
        'total_applications': Application.objects.filter(internship__company=company).count(),
        'open_internships': Internship.objects.filter(company=company).count(),
        'pending_applications': Application.objects.filter(internship__company=company, status='Pending').count(),
    }
    
    return render(request, 'Company_Admin/company_admin_dashboard.html', {'stats': stats, 'company': company})

# Manage Applications (Approve/Reject)
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def manage_applications(request):
    company = request.user.companyadmin.company
    applications = Application.objects.filter(company=company).order_by('-date_applied')
    return render(request, 'company_admin/applications.html', {'applications': applications})

# Assign Supervisor to Application
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def assign_supervisor(request, application_id):
    application = Application.objects.get(id=application_id)
    supervisors = Supervisor.objects.filter(company=application.company)
    
    if request.method == "POST":
        supervisor_id = request.POST.get('supervisor')
        application.supervisor = Supervisor.objects.get(id=supervisor_id)
        application.status = 'Approved'
        application.save()
        messages.success(request, 'Supervisor assigned successfully!')
        return redirect('manage_applications')
    
    return render(request, 'company_admin/assign_supervisor.html', {
        'application': application,
        'supervisors': supervisors
    })

# Toggle Application Status (Open/Close)
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def toggle_applications(request):
    company = request.user.companyadmin.company
    if request.method == "POST":
        company.is_accepting_applications = not company.is_accepting_applications
        company.save()
    return redirect('company_admin_dashboard')

import openai

def suggest_fields(form_type, description):
    prompt = f"Suggest fields for a {form_type} form with the followiCDng description: {description}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip().split(',')
def internship_activity(request):
    # Fetch all internships
    internships = Internship.objects.all()

    # Fetch tasks and evaluations for each internship
    internship_data = []
    for internship in internships:
        tasks = Task.objects.filter(internship=internship)
        evaluations = Evaluation.objects.filter(internship=internship)
        internship_data.append({
            'internship': internship,
            'tasks': tasks,
            'evaluations': evaluations,
        })

    return render(request, 'departement_head/internship_activity.html', {
        'internship_data': internship_data,
    })


def form_list(request):
    forms = FormTemplate.objects.all()
    return render(request, 'departement_head/form_list.html', {'forms': forms})
def generate_evaluation_form(request):
    if request.method == 'POST':
        form = MonthlyPerformanceEvaluationForm(request.POST)
        if form.is_valid():
            # Generate the PDF
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer)

            # Add content to the PDF
            pdf.drawString(100, 800, "ADDIS ABABA SCIENCE AND TECHNOLOGY UNIVERSITY")
            pdf.drawString(100, 780, "INTERNSHIP INDUSTRY SUPERVISOR MONTHLY PERFORMANCE EVALUATION FORMAT")
            pdf.drawString(100, 760, f"Month: {form.cleaned_data['month']}")
            pdf.drawString(100, 740, f"Company Name: {form.cleaned_data['company_name']}")
            pdf.drawString(100, 720, f"Supervisor's Name: {form.cleaned_data['supervisor_name']}")
            pdf.drawString(100, 700, f"Supervisor's Phone No.: {form.cleaned_data['supervisor_phone']}")
            pdf.drawString(100, 680, f"Student's Full Name: {form.cleaned_data['student_name']}")
            pdf.drawString(100, 660, f"Student's ID No.: {form.cleaned_data['student_id']}")
            pdf.drawString(100, 640, f"Student's Department: {form.cleaned_data['student_department']}")

            # General Performance
            pdf.drawString(100, 620, "General Performance (25%)")
            pdf.drawString(120, 600, f"Punctuality (5%): {form.cleaned_data['punctuality']}")
            pdf.drawString(120, 580, f"Reliability (5%): {form.cleaned_data['reliability']}")
            pdf.drawString(120, 560, f"Independence In Work (5%): {form.cleaned_data['independence']}")
            pdf.drawString(120, 540, f"Communication Skills (5%): {form.cleaned_data['communication']}")
            pdf.drawString(120, 520, f"Professionalism (5%): {form.cleaned_data['professionalism']}")

            # Personal Skill
            pdf.drawString(100, 500, "Personal Skill (25%)")
            pdf.drawString(120, 480, f"Speed of Work (5%): {form.cleaned_data['speed_of_work']}")
            pdf.drawString(120, 460, f"Accuracy (5%): {form.cleaned_data['accuracy']}")
            pdf.drawString(120, 440, f"Engagement (5%): {form.cleaned_data['engagement']}")
            pdf.drawString(120, 420, f"Do you need him for your work (5%): {form.cleaned_data['need_for_work']}")
            pdf.drawString(120, 400, f"Cooperation with colleagues (5%): {form.cleaned_data['cooperation']}")

            # Professional Skills
            pdf.drawString(100, 380, "Professional Skills (50%)")
            pdf.drawString(120, 360, f"Technical Skills (5%): {form.cleaned_data['technical_skills']}")
            pdf.drawString(120, 340, f"Organizational Skills (5%): {form.cleaned_data['organizational_skills']}")
            pdf.drawString(120, 320, f"Support of the project tasks (5%): {form.cleaned_data['project_support']}")
            pdf.drawString(120, 300, f"Responsibility in the task fulfillment (15%): {form.cleaned_data['responsibility']}")
            pdf.drawString(120, 280, f"Quality as a team member (20%): {form.cleaned_data['team_quality']}")

            # Additional Comments
            pdf.drawString(100, 260, "Additional Comments:")
            pdf.drawString(120, 240, form.cleaned_data['additional_comments'])

            # Save the PDF
            pdf.save()
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
    else:
        form = MonthlyPerformanceEvaluationForm()

    return render(request, 'departement_head/generate_form.html', {'form': form})

def generate_logbook_form(request):
    if request.method == 'POST':
        form = InternshipLogbookForm(request.POST)
        if form.is_valid():
            # Generate the PDF
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer)

            # Add content to the PDF
            pdf.drawString(100, 800, "ADDIS ABABA SCIENCE AND TECHNOLOGY UNIVERSITY")
            pdf.drawString(100, 780, "INTERNSHIP STUDENT LOGBOOK FORM")
            pdf.drawString(100, 760, f"Student’s Name: {form.cleaned_data['student_name']}")
            pdf.drawString(100, 740, f"Name of Company: {form.cleaned_data['company_name']}")
            pdf.drawString(100, 720, f"Name of Supervisor: {form.cleaned_data['supervisor_name']}")
            pdf.drawString(100, 700, f"Safety Guidelines: {form.cleaned_data['safety_guidelines']}")

            # Logbook Table
            pdf.drawString(100, 680, "| Week | Day | Date | Work Performed | Supervisor’s Signature and Comment |")
            pdf.drawString(100, 660, "|---|---|---|---|---|")

            # Week 1, Day 1
            pdf.drawString(100, 640, f"| 1 | 1 | {form.cleaned_data['week_1_day_1_date']} | {form.cleaned_data['week_1_day_1_work']} | {form.cleaned_data['week_1_day_1_comment']} |")

            # Week 1, Day 2
            pdf.drawString(100, 620, f"| 1 | 2 | {form.cleaned_data['week_1_day_2_date']} | {form.cleaned_data['week_1_day_2_work']} | {form.cleaned_data['week_1_day_2_comment']} |")

            # Add more rows for other days and weeks as needed...

            # Save the PDF
            pdf.save()
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
    else:
        form = InternshipLogbookForm()

    return render(request, 'departement_head/generate_logbook_form.html', {'form': form})

def form_generated(request):
    return render(request, 'departement_head/form_generated.html')
def is_department_head(user):
    return user.is_authenticated and hasattr(user, 'is_department_head') and user.is_department_head


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # System statistics
    total_departments = Department.objects.count()
    total_users = User.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Department management data
    departments = Department.objects.all()
    department_heads = DepartmentHead.objects.select_related('user', 'department')
    
    context = {
        'total_departments': total_departments,
        'total_users': total_users,
        'recent_users': recent_users,
        'departments': departments,
        'department_heads': department_heads,
    }
    return render(request, 'admin/admin_dashboard.html', context)

def company_register(request):
    if request.method == "POST":
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company registered successfully!')
            return redirect('company_admin_dashboard')  # Redirect to the dashboard or another page
    else:
        form = CompanyRegistrationForm()
    return render(request, 'company/register_company.html', {'form': form})

@login_required
def company_management(request):
    companies = Company.objects.all()
    company_names = [company.name for company in companies]
    internships_offered = [Internship.objects.filter(company=company).count() for company in companies]
    applications_received = [Application.objects.filter(company=company).count() for company in companies]
    company_feedbacks = CompanyFeedback.objects.all()

    context = {
        'companies': companies,
        'company_names': company_names,
        'internships_offered': internships_offered,
        'applications_received': applications_received,
        'company_feedbacks': company_feedbacks,
    }
    return render(request, 'company/company_management.html', context)

@login_required
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company added successfully!')
            return redirect('company_management')
    else:
        form = CompanyForm()
    return render(request, 'company/register_company.html', {'form': form})

@login_required
def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated successfully!')
            return redirect('company_management')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'departement_head/edit_company.html', {'form': form, 'company': company})

@login_required
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, 'Company deleted successfully!')
    return redirect('company_management')
def is_department_head(user):
    return user.is_authenticated and hasattr(user, 'is_department_head') and user.is_department_head

@login_required
@user_passes_test(is_department_head)
def view_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    internships = Internship.objects.filter(company=company)
    applications = Application.objects.filter(company=company)
    feedbacks = CompanyFeedback.objects.filter(company=company)

    context = {
        'company': company,
        'internships': internships,
        'applications': applications,
        'feedbacks': feedbacks,
    }
    return render(request, 'company/view_company.html', context)

@login_required
def submit_company_feedback(request):
    if request.method == 'POST':
        form = CompanyFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.submitted_by = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('company_management')
    else:
        form = CompanyFeedbackForm()
    return render(request, 'departement_head/submit_company_feedback.html', {'form': form})

@login_required
def export_company_data(request):
    # Example: Export company data as CSV
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="company_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Industry', 'Location', 'Contact Email', 'Contact Phone', 'Description'])

    companies = Company.objects.all()
    for company in companies:
        writer.writerow([company.name, company.industry, company.location, company.contact_email, company.contact_phone, company.description])

    return response
# Registration Views
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

class StudentRegistrationView(generics.CreateAPIView):
    serializer_class = StudentSerializer

class AdvisorRegistrationView(generics.CreateAPIView):
    serializer_class = AdvisorSerializer

class DepartmentHeadRegistrationView(generics.CreateAPIView):
    serializer_class = DepartmentHeadSerializer

class SupervisorRegistrationView(generics.CreateAPIView):
    serializer_class = SupervisorSerializer

# Browse student list
def student_list(request):
    students = Internship.objects.filter(start_date__year__lt=2024).select_related('student')
    return render(request, 'students/student_list.html', {'students': students})


@login_required
def student_management(request):
    # Ensure the user is a department head
    if not request.user.is_department_head:
        return redirect('home')

    # Get the department head's department
    department_head = get_object_or_404(DepartmentHead, user=request.user)
    department = department_head.department

    # Fetch all students in the department
    students = Student.objects.filter(department=department)

    # Debug: Print students and their IDs
    for student in students:
        print(f"Student ID: {student.user.id}, Name: {student.user.get_full_name()}")

    context = {
        'students': students,
    }
    return render(request, 'students/student_management.html', context)
@login_required
def submit_feedback(request, user_id):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        student = get_object_or_404(Student, user_id=user_id)

        # Save feedback
        Feedback.objects.create(
            student=student,
            feedback=feedback_text,
            submitted_by=request.user
        )

        messages.success(request, 'Feedback submitted successfully!')
        return redirect('view_student_progress', user_id=user_id)


@login_required
def export_student_progress(request, user_id):
    # Fetch the student
    student = get_object_or_404(Student, user_id=user_id)

    # Fetch the student's internships through their applications
    internships = Internship.objects.filter(application__student=student)

    # Create a PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 800, f"Progress Report for {student.user.get_full_name()}")

    y = 780
    for internship in internships:
        pdf.drawString(100, y, f"Internship at {internship.company.name}")
        y -= 20
        tasks = Task.objects.filter(internship=internship)
        for task in tasks:
            pdf.drawString(120, y, f"Task: {task.description} - Status: {task.status}")
            y -= 15
        y -= 10

    pdf.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
@login_required
def view_student_progress(request, user_id):
    # Fetch the student
    student = get_object_or_404(Student, user_id=user_id)

    # Fetch the student's applications
    applications = Application.objects.filter(student=student)

    # Fetch internships associated with the student's applications
    internships = Internship.objects.filter(application__student=student)

    # Fetch tasks and evaluations for each internship
    progress_data = []
    completed_tasks = 0
    pending_tasks = 0
    evaluation_dates = []
    evaluation_scores = []

    for internship in internships:
        tasks = Task.objects.filter(internship=internship)
        evaluations = Evaluation.objects.filter(internship=internship)

        # Count completed and pending tasks
        completed_tasks += tasks.filter(status='Completed').count()
        pending_tasks += tasks.filter(status='Pending').count()

        # Collect evaluation data
        for evaluation in evaluations:
            evaluation_dates.append(evaluation.date.strftime('%Y-%m-%d'))
            evaluation_scores.append(float(evaluation.score))

        progress_data.append({
            'internship': internship,
            'tasks': tasks,
            'evaluations': evaluations,
        })

    context = {
        'student': student,
        'progress_data': progress_data,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'evaluation_dates': evaluation_dates,
        'evaluation_scores': evaluation_scores,
    }
    return render(request, 'students/view_student_progress.html', context)
@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('student_management')
    else:
        form = StudentRegistrationForm()
    return render(request, 'students/add_student.html', {'form': form})

@login_required
def view_student(request, student_id):
    student = get_object_or_404(Student, user_id=student_id)
    return render(request, 'students/view_student.html', {'student': student})

@login_required
def edit_student(request, student_user_id):
    student = get_object_or_404(Student, user_id=student_user_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_management')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/edit_student.html', {'form': form})

@login_required
def delete_student(request, student_user_id):
    student = get_object_or_404(Student, user_id=student_user_id)
    student.delete()
    return redirect('student_management')
# Dashboards
@login_required
def student_dashboard(request):
    return render(request, 'students/student_dashboard.html', {'user': request.user})

@login_required
def department_head_dashboard(request):
    return render(request, 'departement_head/department_head_dashboard.html', {'user': request.user})

@login_required
def industry_supervisor_dashboard(request):
    return render(request, 'supervisor/industry_supervisor_dashboard.html', {'user': request.user})

@login_required
def advisor_dashboard(request):
    return render(request, 'advisors/advisor_dashboard.html', {'user': request.user})

# Registration Views for All Actors
def student_register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Save the user and related data
            login(request, user)
            messages.success(request, 'Student registered successfully!')
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'students/student_register.html', {'form': form})

def register_department(request):
    if request.method == 'POST':
        form = DepartmentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department registered successfully!")
            return redirect('')
    else:
        form = DepartmentRegistrationForm()

    return render(request, 'department/register_department.html', {'form': form})

def department_head_register(request):
    if request.method == "POST":
        form = DepartmentHeadRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Department Head registered successfully!')
                return redirect('department_head_dashboard')
            except Exception as e:
                messages.error(request, f'Error saving data: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = DepartmentHeadRegistrationForm()
    
    return render(request, 'departement_head/department_head_register.html', {
        'form': form,
        'departments': Department.objects.all()
    })
def supervisor_register(request):
    if request.method == "POST":
        form = SupervisorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data
            messages.success(request, 'Supervisor registered successfully!')
            return redirect('admin_dashboard')
        else:
            print("Form errors:", form.errors)  # Debugging
    else:
        form = SupervisorRegistrationForm()
    return render(request, 'supervisor/supervisor_register.html', {'form': form})

@login_required
def internship_applications(request):
    return render(request, 'internship_applications.html')

@login_required
def progress_reports(request):
    return render(request, 'progress_reports.html')

@login_required
def feedback(request):
    return render(request, 'feedback.html')

@login_required
def request_support(request):
    return render(request, 'request_support.html')

@login_required
def final_report(request):
    return render(request, 'final_report.html')

@login_required
def manage_placements(request):
    return render(request, 'manage_placements.html')

@login_required
def student_progress(request):
    return render(request, 'student_progress.html')

@login_required
def generate_reports(request):
    return render(request, 'generate_reports.html')

@login_required
def set_policies(request):
    return render(request, 'set_policies.html')

@login_required
def assigned_students(request):
    return render(request, 'assigned_students.html')

@login_required
def manage_tasks(request):
    return render(request, 'manage_tasks.html')

@login_required
def monitor_performance(request):
    return render(request, 'monitor_performance.html')

@login_required
def provide_feedback(request):
    return render(request, 'provide_feedback.html')

@login_required
def communication(request):
    return render(request, 'communication.html')

@login_required
def review_applications(request):
    return render(request, 'review_applications.html')

@login_required
def reports(request):
    return render(request, 'reports.html')

@login_required
def give_feedback(request):
    return render(request, 'give_feedback.html')

@login_required
def performance_evaluation(request):
    return render(request, 'performance_evaluation.html')

# API ViewSets
class DepartmentHeadViewSet(viewsets.ModelViewSet):
    queryset = DepartmentHead.objects.all()
    serializer_class = DepartmentHeadSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class AdvisorViewSet(viewsets.ModelViewSet):
    queryset = Advisor.objects.all()
    serializer_class = AdvisorSerializer

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

class InternshipViewSet(viewsets.ModelViewSet):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer