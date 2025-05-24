from rest_framework import viewsets, generics
from django.shortcuts import render, redirect
from dateutil.relativedelta import relativedelta
from django.core.exceptions import PermissionDenied
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
from django.views.decorators.http import require_POST
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import Avg
from django.db.models import Exists, OuterRef
from django.db.models import Subquery, OuterRef
from .models import *
from datetime import datetime
from django.http import JsonResponse
import myapp.templatetags.custom_filters
from django.db.models import Q
from .models import Feedback,CompanyFeedback,ChatMessage, PrivateMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
import openai
from .serializers import *
from .models import UserRole
from .forms import *
    
def home(request):
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'home.html')
# 🧠 Django view for chatbot
def chatbot_page(request):
    return render(request, 'chatbot.html')
# myapp/views.py

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt  # Only if you don’t have CSRF protection on this endpoint
def get_chatbot_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)

    try:
        data = json.loads(request.body)

        # TODO: Replace with your auth system info if available
        name = data.get("name", "aastu internship")
        email = data.get("email", "gosayewoyo5@gmail.com")

        API_KEY = "8b5bd9b2b09a88c650af07f9ad55ddd8ec4307291ed841d465e62bb019e3fa77"
        CHATBOT_ID = "c5a86b06ff9659387653984b5528cd54"

        response = requests.post(
            "https://www.askyourdatabase.com/api/chatbot/v2/session",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            },
            json={
                "chatbotid": CHATBOT_ID,
                "name": name,
                "email": email,
            },
        )

        if response.status_code == 200:
            session_url = response.json().get("url")
            if session_url:
                return JsonResponse({"url": session_url})
            else:
                return JsonResponse({"error": "No URL returned by API"}, status=500)
        else:
            return JsonResponse({
                "error": "Failed to create chatbot session",
                "status_code": response.status_code,
                "response": response.text,
            }, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": "Unexpected error", "details": str(e)}, status=500)


import jwt
from datetime import datetime, timedelta
from django.conf import settings

def internship_list(request):
    def generate_chat_token(user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    context = {
        'internships': Internship.objects.all(),
        'chat_token': generate_chat_token(request.user)
    }
    return render(request, 'internships.html', context)
# views.py
from django.views.generic import DetailView
from .models import Company, CompanyRating

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company/company_detail.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.get_object()
        
        # Add rating information
        context['ratings'] = CompanyRating.objects.filter(company=company)
        context['average_rating'] = company.average_rating
        context['total_ratings'] = company.rating_count
        
        # Add internship information
        context['internships'] = company.internship_set.filter(is_open=False)
        
        # Check if current user has rated
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student'):
            context['has_rated'] = CompanyRating.objects.filter(
                company=company,
                student=self.request.user.student
            ).exists()
        
        return context
@login_required
@user_passes_test(lambda u: u.is_department_head)
def advisor_assigned_student_departmenet_head(request, advisor_id):
    # Get the advisor
    advisor = get_object_or_404(Advisor, user_id=advisor_id)
    
    # Get the students assigned to this advisor
    assigned_students = Student.objects.filter(assigned_advisor=advisor)
    
    # Pass the data to the template
    return render(request, 'students/advisor_assigned_students.html', {
        'advisor': advisor,
        'assigned_students': assigned_students,
    })

@login_required
@user_passes_test(lambda u: u.is_advisor)
def advisor_assigned_students(request, advisor_id):
    # Get the advisor
    advisor = get_object_or_404(Advisor, user_id=advisor_id)
    
    # Get the students assigned to this advisor
    assigned_students = Student.objects.filter(assigned_advisor=advisor)
    
    # Pass the data to the template
    return render(request, 'advisors/assigned_students.html', {
        'advisor': advisor,
        'assigned_students': assigned_students,
    })
@login_required
@user_passes_test(lambda u: u.is_department_head)
def assign_advisor(request, student_user_id):
    student = get_object_or_404(Student, user_id=student_user_id)
    if request.method == 'POST':
        form = AssignAdvisorForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Advisor assigned successfully!')
            return redirect('student_management')
    else:
        form = AssignAdvisorForm(instance=student)
    return render(request, 'advisors/assign_advisor.html', {'form': form, 'student': student})

@login_required
def communication_page(request):
    return render(request, 'departement_head/communication_page.html')
from .utils.token_utils import generate_chat_token
@login_required
def existing_internships(request):
    user = request.user
    internships = Internship.objects.all()
    token = generate_chat_token(user)
    applied_internship_ids = []
    locations = Company.objects.values_list('location', flat=True).distinct()
    internship_titles = Internship.objects.values_list('title', flat=True).distinct()  # NEW LINE

    if hasattr(request.user, 'student'):
        student = request.user.student
        applied_internship_ids = Application.objects.filter(
            student=student
        ).values_list('internship_id', flat=True)

    context = {
        'internships': internships,
        'chatbot_token': token,
        'applied_internship_ids': applied_internship_ids,
        'locations': locations,
        'internship_titles': internship_titles  # ADD THIS TO CONTEXT
    }
    return render(request, 'company/existing_internships.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Internship, Application

@login_required
def internship_detail(request, pk):
    internship = get_object_or_404(Internship, pk=pk)

    # Determine if the logged-in user is a student
    is_student = hasattr(request.user, 'student')
    has_applied = False

    if is_student:
        student = request.user.student
        has_applied = Application.objects.filter(internship=internship, student=student).exists()

    # Determine base template based on user role
    user = request.user
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    context = {
        'internship': internship,
        'is_student': is_student,
        'has_applied': has_applied,
        'base_template': base_template,
    }
    return render(request, 'company/internship_detail.html', context)


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

@login_required
@user_passes_test(lambda u: u.is_company_admin)  # Ensure that only company admins can post internships
def post_internship(request):
    # Get the company_admin instance for the logged-in user
    company_admin = CompanyAdmin.objects.get(user=request.user)

    if request.method == 'POST':
        # Pass the company_admin to the form during instantiation
        form = InternshipForm(request.POST, request.FILES, company_admin=company_admin)
        if form.is_valid():
            form.save()
            messages.success(request, 'Internship posted successfully!')
            return redirect('company_admin_dashboard')
    else:
        # On GET request, pass company_admin to the form
        form = InternshipForm(company_admin=company_admin)

    return render(request, 'company/post_internship.html', {'form': form})

def view_internships(request):
    internships = Internship.objects.filter(
        company=request.user.companyadmin.company
    ).annotate(applicant_count=Count('applications'))  # ✅ Now this works
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

@login_required
def apply_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)

    # Ensure only students can apply
    if not hasattr(request.user, 'student'):
        messages.error(request, "Only students can apply for internships.")
        return redirect('existing_internships')

    student = request.user.student

    # Check if already applied
    if Application.objects.filter(internship=internship, student=student).exists():
        messages.error(request, "You have already applied to this internship.")
        return redirect('existing_internships')

    # Check qualification match
    student_info = f"{student.major}, Year {student.year}"
    matched_qualifications = []
    missing_qualifications = []

    for q in internship.required_qualifications:
        if q.lower() in student_info.lower():
            matched_qualifications.append(q)
        else:
            missing_qualifications.append(q)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.student = student
            application.save()
            messages.success(request, "Your application has been submitted!")
            return redirect('existing_internships')
        else:
            messages.error(request, "There was an error with your application.")
    else:
        form = ApplicationForm()

    context = {
        'internship': internship,
        'form': form,
        'matched_qualifications': matched_qualifications,
        'missing_qualifications': missing_qualifications,
    }
    return render(request, 'students/apply_internship.html', context)

    
@login_required
def communication_dash(request):
    # Determine base template based on user role
    user = request.user
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    is_advisor = getattr(user, "is_advisor", False)
    is_supervisor = getattr(user, "is_supervisor", False)

    return render(request, 'Supervisor/communication_dashboard.html', {
        'base_template': base_template,
        'is_advisor': is_advisor,
        'is_supervisor': is_supervisor
    })
@login_required
def applicant_list(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)

    user = request.user
    is_dept_head = getattr(user, "is_department_head", False)

    # Base template selection
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif is_dept_head:
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    # Filter applications
    if is_dept_head and hasattr(user, 'departmenthead'):
        department = user.departmenthead.department
        applications = Application.objects.filter(
            internship=internship,
            student__department=department
        ).select_related('student__user')
    else:
        applications = Application.objects.filter(
            internship=internship
        ).select_related('student__user')

    # Prepare applicant data
    applicants = []
    for application in applications:
        student = application.student
        applicants.append({
            'name': f"{student.user.first_name} {student.user.last_name}",
            'email': student.user.email,
            'id': application.id,
            'status': application.status,
        })

    context = {
        'internship': internship,
        'applicants': applicants,
        'base_template': base_template,
    }
    return render(request, 'company/applicant_list.html', context)
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    internship = application.internship

    required_list = []
    if internship.required_qualifications:
        required_list = [q.strip() for q in internship.required_qualifications.split(',') if q.strip()]

    optional_list = []
    if internship.optional_qualifications:
        optional_list = [q.strip() for q in internship.optional_qualifications.split(',') if q.strip()]

    return render(request, 'company_admin/application_detail.html', {
        'application': application,
        'required_list': required_list,
        'optional_list': optional_list,
    })

from django.core.exceptions import ObjectDoesNotExist

@login_required
def apply_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)

    try:
        student = request.user.student
    except ObjectDoesNotExist:
        messages.error(request, "Only students can apply for internships.")
        return redirect('existing_internships')

    if Application.objects.filter(internship=internship, student=student).exists():
        messages.warning(request, "You have already submitted an application for this internship.")
        return redirect('existing_internships')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES, internship=internship, student=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
            print("Form errors:", form.errors)  # Debug
    else:
        form = ApplicationForm(internship=internship, student=student)

    return render(request, 'students/apply_internship.html', {
        'internship': internship,
        'form': form
    })

@login_required
def list_students_for_permission(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    students = Student.objects.filter(
        application__internship=internship,
        application__status='Approved'
    ).distinct()

    return render(request, 'departement_head/list_students.html', {
        'internship': internship,
        'students': students,
    })

@login_required
@user_passes_test(lambda u: hasattr(u, 'departmenthead'))  # Only Department Heads
def list_internships_for_permission(request):
    department_head = request.user.departmenthead

    internships = Internship.objects.filter(
        application__status='Approved',
        application__student__department=department_head.department
    ).distinct()

    return render(request, 'departement_head/list_internships.html', {
        'internships': internships,
    })

@login_required
def chat_with_company_admin(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company_admins = CompanyAdmin.objects.filter(company=company)
    
    if not company_admins.exists():
        messages.error(request, "No company admin found for this company.")
        return redirect('view_company', company_id=company_id)

    # Assuming a one-to-one chat with the first company admin
    company_admin = company_admins.first()

    return redirect('private_chat', user_id=company_admin.user.id)

def company_supervisors(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    supervisors = Supervisor.objects.filter(company=company)  # Ensure this query is correct

    return render(request, 'supervisor/supervisors.html', {
        'company': company,
        'supervisors': supervisors
    })


@login_required
def private_chat_list(request, role):
    """Displays a list of users the logged-in user can chat with, based on their role."""
    users = []
    user = request.user

    # Determine base template based on user role
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    # Department Head Logic
    if hasattr(user, 'departmenthead'):
        department = user.departmenthead.department

        if role == 'supervisors':
            users = Supervisor.objects.filter(
                assigned__student__department=department
            ).distinct()
        elif role == 'advisors':
            users = Advisor.objects.filter(department=department).distinct()
        elif role == 'company_admins':
            users = CompanyAdmin.objects.filter(
                company__internship__application__student__department=department,
                company__internship__application__status='Approved'
            ).distinct()

    # Advisor Logic
    elif hasattr(user, 'advisor'):
        advisor = user.advisor
        department = advisor.department

        if role == 'department_heads':
            users = DepartmentHead.objects.filter(department=department)
        elif role == 'supervisors':
            users = Supervisor.objects.filter(
                student__assigned_advisor=advisor
            ).distinct()

    # Supervisor Logic
    elif hasattr(user, 'supervisor'):
        supervisor = user.supervisor

        if role == 'advisors':
            users = Advisor.objects.filter(
                student__assigned_supervisor=supervisor
            ).distinct()
        elif role == 'department_heads':
            users = DepartmentHead.objects.filter(
                department__student__assigned_supervisor=supervisor
            ).distinct()

    # Company Admin Logic
    elif hasattr(user, 'companyadmin'):
        company = user.companyadmin.company

        if role == 'department_heads':
            users = DepartmentHead.objects.filter(
                department__student__application__internship__company=company,
                department__student__application__status='Approved'
            ).distinct()

    return render(request, 'private_chat_list.html', {
        'users': users,
        'role': role,
        'base_template': base_template
    })

@login_required
def private_chat(request, user_id):
    if request.user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(request.user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(request.user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(request.user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(request.user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(request.user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    receiver = get_object_or_404(User, id=user_id)
    sender = request.user
    allowed = False

    # Department Head
    if hasattr(sender, 'departmenthead'):
        department = sender.departmenthead.department
        if hasattr(receiver, 'supervisor'):
            allowed = Application.objects.filter(
                internship__company=receiver.supervisor.company,
                student__department=department,
                status='Approved'
            ).exists()
        elif hasattr(receiver, 'companyadmin'):
            allowed = Application.objects.filter(
                internship__company=receiver.companyadmin.company,
                student__department=department,
                status='Approved'
            ).exists()
        elif hasattr(receiver, 'advisor'):
            allowed = department == receiver.advisor.department

    # Advisor
    elif hasattr(sender, 'advisor'):
        advisor = sender.advisor
        if hasattr(receiver, 'departmenthead'):
            allowed = advisor.department == receiver.departmenthead.department
        elif hasattr(receiver, 'supervisor'):
            allowed = Student.objects.filter(
                assigned_advisor=advisor,
                assigned_supervisor=receiver.supervisor
            ).exists()

    # Supervisor
    elif hasattr(sender, 'supervisor'):
        supervisor = sender.supervisor
        if hasattr(receiver, 'advisor'):
            allowed = Student.objects.filter(
                assigned_supervisor=supervisor,
                assigned_advisor=receiver.advisor
            ).exists()
        elif hasattr(receiver, 'departmenthead'):
            allowed = Student.objects.filter(
                assigned_supervisor=supervisor,
                department=receiver.departmenthead.department
            ).exists()

    # Company Admin
    elif hasattr(sender, 'companyadmin'):
        company = sender.companyadmin.company
        if hasattr(receiver, 'departmenthead'):
            allowed = Application.objects.filter(
                internship__company=company,
                student__department=receiver.departmenthead.department,
                status='Approved'
            ).exists()

    if not allowed:
        messages.error(request, "You are not allowed to chat with this user.")
        return redirect('dashboard_redirect')

    # Handle POST
    if request.method == 'POST':
        message_content = request.POST.get('message')
        file = request.FILES.get('file')

        if message_content or file:
            message_type = 'text'
            if file:
                if file.content_type.startswith('image'):
                    message_type = 'image'
                elif file.content_type.startswith('video'):
                    message_type = 'video'
                else:
                    message_type = 'file'

            PrivateMessage.objects.create(
                sender=sender,
                receiver=receiver,
                content=message_content,
                file=file,
                message_type=message_type
            )
            messages.success(request, "Message sent successfully!")
        else:
            messages.warning(request, "Message cannot be empty!")
        return redirect('private_chat', user_id=user_id)

    chat_messages = PrivateMessage.objects.filter(
        Q(sender=sender, receiver=receiver) |
        Q(sender=receiver, receiver=sender)
    ).order_by('timestamp')

    return render(request, 'departement_head/private_chat.html', {
        'receiver': receiver,
        'chat_messages': chat_messages,
        'base_template': base_template
    })
@login_required
def clear_chat_history(request, user_id):
    """
    Clears the chat history between the logged-in user and the specified user.
    """
    receiver = get_object_or_404(User, id=user_id)
    
    # Ensure the user has permission to clear the chat history
    allowed = False
    sender = request.user

    # Department Head Chat Permissions
    if hasattr(sender, 'departmenthead'):
        department = sender.departmenthead.department

        if hasattr(receiver, 'supervisor'):
            allowed = Application.objects.filter(
                internship__company=receiver.supervisor.company,
                student__department=department,
                status='Approved'
            ).exists()

        elif hasattr(receiver, 'companyadmin'):
            allowed = Application.objects.filter(
                internship__company=receiver.companyadmin.company,
                student__department=department,
                status='Approved'
            ).exists()
        elif hasattr(receiver, 'advisor'):
            allowed = sender.departmenthead.department == receiver.advisor.department

    # Advisor Chat Permissions
    elif hasattr(sender, 'advisor'):
        advisor = sender.advisor

        if hasattr(receiver, 'departmenthead'):
            allowed = advisor.department == receiver.departmenthead.department

        elif hasattr(receiver, 'supervisor'):
            allowed = Student.objects.filter(
                assigned_advisor=advisor,
                assigned_supervisor=receiver.supervisor
            ).exists()

    # Supervisor Chat Permissions
    elif hasattr(sender, 'supervisor'):
        supervisor = sender.supervisor

        if hasattr(receiver, 'advisor'):
            allowed = Student.objects.filter(
                assigned_supervisor=supervisor,
                assigned_advisor=receiver.advisor
            ).exists()

        elif hasattr(receiver, 'departmenthead'):
            allowed = Student.objects.filter(
                assigned_supervisor=supervisor,
                department=receiver.departmenthead.department
            ).exists()

    # Company Admin Chat Permissions
    elif hasattr(sender, 'companyadmin'):
        company = sender.companyadmin.company

        if hasattr(receiver, 'departmenthead'):
            allowed = Application.objects.filter(
                internship__company=company,
                student__department=receiver.departmenthead.department,
                status='Approved'
            ).exists()

    if not allowed:
        messages.error(request, "You are not allowed to clear chat history with this user.")
        return redirect('dashboard_redirect')

    # Delete all messages between the sender and receiver
    PrivateMessage.objects.filter(
        Q(sender=sender, receiver=receiver) |
        Q(sender=receiver, receiver=sender)
    ).delete()

    messages.success(request, "Chat history cleared successfully!")
    return redirect('private_chat', user_id=user_id)

@login_required
def group_chat(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)

    # Determine base template based on user role
    user = request.user
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    # Permission check
    if not group.can_communicate(user):
        messages.error(request, "You don't have permission to access this group")
        return redirect('communication_page')

    # Handle message post
    if request.method == 'POST':
        form = GroupMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            message.group = group

            # Determine message type
            if message.file:
                file_type = message.file.name.split('.')[-1].lower()
                if file_type in ['jpg', 'jpeg', 'png', 'gif']:
                    message.message_type = 'image'
                elif file_type in ['mp4', 'mov', 'avi']:
                    message.message_type = 'video'
                else:
                    message.message_type = 'file'
            else:
                message.message_type = 'text'

            message.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'file_url': message.file.url if message.file else None,
                        'message_type': message.message_type,
                        'sender': user.username,
                        'timestamp': message.timestamp.isoformat()
                    }
                })
            return redirect('group_chat', group_id=group.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)

    # Fetch messages and form
    messages = GroupMessage.objects.filter(group=group).order_by('timestamp')
    form = GroupMessageForm()

    return render(request, 'departement_head/group_chat.html', {
        'group': group,
        'messages': messages,
        'form': form,
        'base_template': base_template
    })
@login_required
@user_passes_test(lambda u: u.is_department_head)
def create_department_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.created_by_role = 'department_head'
            group.department = request.user.departmenthead.department
            group.save()
            
            # Add participants: students in the department AND the department head
            group.add_participants()  # Adds students
            group.participants.add(request.user)  # Add department head as a participant
            
            messages.success(request, "Department group created successfully!")
            return redirect('group_chat', group_id=group.id)
    else:
        form = ChatGroupForm()
    
    return render(request, 'departement_head/create_department.html', {'form': form})

# Advisor Group Creation
# views.py
@login_required
@user_passes_test(lambda u: u.is_advisor)
def create_advisor_group(request):
    advisor = request.user.advisor  # Get the logged-in advisor

    if request.method == 'POST':
        form = AdvisorChatGroupForm(request.POST, advisor=advisor)
        if form.is_valid():
            group = form.save()
            messages.success(request, "Advisor group created successfully!")
            return redirect('group_chat', group_id=group.id)
    else:
        form = AdvisorChatGroupForm(advisor=advisor)
    
    return render(request, 'advisors/create_advisor.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_supervisor)
def create_supervisor_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.created_by_role = 'supervisor'
            group.supervisor = request.user.supervisor
            group.save()
            
            # Automatically add participants
            group.add_participants()
            
            messages.success(request, "Supervisor group created successfully!")
            return redirect('group_chat', group_id=group.id)
    else:
        form = ChatGroupForm()
    
    return render(request, 'Supervisor/create_supervisor.html', {'form': form})
@login_required
@user_passes_test(lambda u: u.is_student)
def create_student_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.created_by_role = 'student'
            group.internship = request.user.student.internship
            group.save()
            
            # Automatically add participants
            group.add_participants()
            
            messages.success(request, "Student group created successfully!")
            return redirect('group_chat', group_id=group.id)
    else:
        form = ChatGroupForm()
    
    return render(request, 'students/create_student.html', {'form': form})

@login_required
def list_chat_groups(request):
    user = request.user
    groups = ChatGroup.objects.none()

    # Determine base template
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    # Fetch groups based on role
    if getattr(user, "is_department_head", False):
        department = user.departmenthead.department
        groups = ChatGroup.objects.filter(
            Q(department=department) |
            Q(participants=user)
        )
    elif getattr(user, "is_student", False):
        department = user.student.department
        groups = ChatGroup.objects.filter(
            Q(department=department) |
            Q(participants=user)
        )
    elif getattr(user, "is_advisor", False):
        groups = ChatGroup.objects.filter(
            Q(advisor=user.advisor) |
            Q(participants=user)
        )
    elif getattr(user, "is_supervisor", False):
        groups = ChatGroup.objects.filter(
            Q(supervisor=user.supervisor) |
            Q(participants=user)
        )

    return render(request, 'departement_head/list_chat_groups.html', {
        'groups': groups.distinct().order_by('-created_at'),
        'base_template': base_template
    })

from django.views.decorators.csrf import csrf_exempt
@login_required
@csrf_exempt
def send_group_message(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    
    if not group.can_communicate(request.user):
        return JsonResponse({"status": "error", "message": "Permission denied"}, status=403)

    if request.method == "POST":
        form = GroupMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            
            # Handle file upload and set message type
            if 'file' in request.FILES:
                file = request.FILES['file']
                message.file = file
                
                # Determine message type based on file content type
                if file.content_type.startswith('image'):
                    message.message_type = 'image'
                elif file.content_type.startswith('video'):
                    message.message_type = 'video'
                else:
                    message.message_type = 'file'
            else:
                message.message_type = 'text'
                
            message.save()
            
            # Mark message as read by sender
            message.read_by.add(request.user)
            
            # Prepare response data
            response_data = {
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'file_url': message.file.url if message.file else None,
                    'file_name': message.file.name if message.file else None,
                    'file_size': message.file.size if message.file else None,
                    'message_type': message.message_type,
                    'sender': request.user.username,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'is_sender': True,
                    'is_admin': request.user in group.admins.all(),
                    'read': False
                }
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# views.py
@login_required
@require_POST
def edit_message(request, message_id):
    message = get_object_or_404(GroupMessage, id=message_id)
    
    if message.sender != request.user and not request.user in message.group.admins.all():
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    form = GroupMessageForm(request.POST, request.FILES, instance=message)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'errors': form.errors})

@login_required
@require_POST
def delete_message(request, message_id):
    message = get_object_or_404(GroupMessage, id=message_id)
    
    if message.sender != request.user and not request.user in message.group.admins.all():
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    message.soft_delete()
    return JsonResponse({'status': 'success'})
@login_required
def manage_group(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    
    if not group.can_edit(request.user):
        messages.error(request, "You don't have permission to manage this group")
        return redirect('list_chat_groups')
    
    if request.method == 'POST':
        if 'delete_group' in request.POST:
            group.soft_delete()
            messages.success(request, "Group deleted successfully")
            return redirect('list_chat_groups')
        
        form = ChatGroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated successfully")
            return redirect('group_chat', group_id=group.id)
    
    return render(request, 'groups/manage.html', {
        'group': group,
        'form': ChatGroupForm(instance=group)
    })


from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404

User = get_user_model()

def profile(request, user_id=None):
    # The user being viewed
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user

    # Logged-in user (for header)
    logged_in_user = request.user
    is_own_profile = (logged_in_user == user)

    # Choose base template by role (based on logged-in user)
    if logged_in_user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(logged_in_user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(logged_in_user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(logged_in_user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(logged_in_user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(logged_in_user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"

    student_profile = getattr(user, 'student', None) if getattr(user, 'is_student', False) else None

    context = {
        "user": user,  # The profile being viewed
        "logged_in_user": logged_in_user,  # Always the current user
        "is_own_profile": is_own_profile,
        "base_template": base_template,
        "student_profile": student_profile,
    }

    return render(request, "departement_head/profile.html", context)




@login_required
def edit_profile(request):
    user = request.user

    # Determine base template based on user role
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"  # Default fallback template

    if request.method == "POST":
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        user.bio = request.POST.get("bio")
        user.address = request.POST.get("address")

        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]
            print("Profile image uploaded.")

        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "departement_head/edit_profile.html", {"base_template": base_template})


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
    form_class = SuperadminStudentForm
    template_name = 'form.html'  # Template for the form
    success_url = reverse_lazy('admin_dashboard')  # Redirect to admin dashboard after creation

    def test_func(self):
        """Ensure only superusers can create users."""
        return self.request.user.is_superuser

    def form_valid(self, form):
        """Set additional fields or perform actions before saving the user."""
        messages.success(self.request, 'User created successfully!')
        return super().form_valid(form)

from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth import get_user_model

User = get_user_model()

class UserUpdateView(UpdateView):
    model = User
    template_name = 'form.html'
    success_url = reverse_lazy('admin_dashboard')  # adjust as needed

    def get_form_class(self):
        user = self.get_object()
        if user.is_student:
            return SuperadminStudentUpdateForm
        elif user.is_advisor:
            return SuperadminAdvisorUpdateForm
        elif user.is_supervisor:
            return SuperadminSupervisorUpdateForm
        elif user.is_department_head:
            return DepartmentHeadUpdateForm
        elif user.is_company_admin:
            return CompanyAdminUpdateForm
        return BaseUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ✅ Fix: Ensure logged_in_user is in context so admin_base.html won't break
        context['logged_in_user'] = self.request.user
        return context

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
    advisors = Advisor.objects.filter(department=department).annotate(student_count=Count('student'))
    return render(request, 'advisors/advisor_management.html', {
        'advisors': advisors,
        'departments': Department.objects.all()
    })
@login_required
def advisor_register(request):
    user = request.user

    # Determine base template based on role
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    else:
        return redirect('unauthorized_access')

    # Superadmin case
    if user.is_superuser:
        if request.method == 'POST':
            form = SuperadminAdvisorForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Advisor registered successfully!')
                return redirect('admin_dashboard')  # Or any appropriate view
        else:
            form = SuperadminAdvisorForm()

    # Department Head case
    elif hasattr(user, 'departmenthead'):
        department = user.departmenthead.department
        if request.method == 'POST':
            form = DepartmentHeadAdvisorForm(request.POST, request.FILES, department=department)
            if form.is_valid():
                form.save()
                messages.success(request, 'Advisor registered successfully!')
                return redirect('advisor_management')  # Or any appropriate view
        else:
            form = DepartmentHeadAdvisorForm(department=department)

    return render(request, 'advisors/advisor_register.html', {
        'form': form,
        'base_template': base_template,
        'is_superuser': user.is_superuser
    })

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
def update_advisor(request, advisor_user_id):
    advisor = get_object_or_404(Advisor, user_id=advisor_user_id)
    if request.method == 'POST':
        form = DepartmentHeadAdvisorUpdateForm(request.POST, request.FILES, instance=advisor)
        if form.is_valid():
            form.save()
            return redirect('advisor_management')
    else:
        form = DepartmentHeadAdvisorUpdateForm(instance=advisor)
    return render(request, 'advisors/update_advisor.html', {'form': form})


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
    model = Notification
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
    model = MonthlyEvaluation
    template_name = 'evaluation/list.html'
    context_object_name = 'evaluations'

class EvaluationCreateView(CRUDMixin, AdminRequiredMixin, CreateView):
    model = MonthlyEvaluation
    form_class = MonthlyEvaluationForm
    success_url = reverse_lazy('evaluation_list')

# Create similar classes for all other models...
@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')   # Redirect to Django admin dashboard
    if hasattr(request.user, 'is_company_admin') and request.user.is_company_admin:
        return redirect('company_admin_dashboard')
    elif hasattr(request.user, 'is_student') and request.user.is_student:
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
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def company_admin_dashboard(request):
    company = request.user.companyadmin.company  # Get the admin's company

    stats = {
        'total_applications': Application.objects.filter(internship__company=company).count(),
        'open_internships': Internship.objects.filter(company=company).count(),
        'pending_applications': Application.objects.filter(internship__company=company, status='Pending').count(),
        'supervisor_count': Supervisor.objects.filter(company=company).count(),  # Count supervisors
    }

    return render(request, 'Company_Admin/company_admin_dashboard.html', {
        'stats': stats,
        'company': company
    })
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
def assign_supervisor_to_students(request):
    # Get the company of the logged-in company admin
    company_admin = request.user.companyadmin
    company = company_admin.company

    # Fetch students with approved applications for this company
    students = Student.objects.filter(
        application__internship__company=company,
        application__status='Approved'
    ).distinct()

    # Fetch supervisors for the company
    supervisors = Supervisor.objects.filter(company=company)

    # Initialize the form with the company
    form = AssignSupervisorForm(company=company)

    if request.method == 'POST':
        # Bind the form to the POST data
        form = AssignSupervisorForm(request.POST, company=company)
        if form.is_valid():
            # Get the selected student and supervisor
            student = form.cleaned_data['student']
            supervisor = form.cleaned_data['supervisor']

            # Assign the supervisor to the student
            student.assigned_supervisor = supervisor
            student.save()

            # Show a success message
            messages.success(request, f"Supervisor {supervisor.user.get_full_name()} assigned to {student.user.get_full_name()}.")
            return redirect('company_admin_dashboard')  # Redirect to the dashboard
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'company_admin/assign_supervisor.html', {
        'form': form,
        'students': students,  # ✅ Add students to the template context
        'supervisors': supervisors,  # ✅ Add supervisors to the template context
    })
@login_required
def assigned_students(request):
    # Ensure the user is a supervisor
    if not request.user.is_supervisor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('supervisor_dashboard')

    # Get the supervisor object
    supervisor = get_object_or_404(Supervisor, user=request.user)

    # Get students assigned to this supervisor
    assigned_students = Student.objects.filter(assigned_supervisor=supervisor).select_related('user')

    return render(request, 'Supervisor/assigned_students.html', {
        'advisor': supervisor,  # ✅ Matches what your template uses
        'assigned_students': assigned_students,  # ✅ Matches what your template expects
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
        
        internship_data.append({
            'internship': internship,
            'tasks': tasks,
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

def is_admin(user):
    return user.is_authenticated and user.is_superuser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, OuterRef, Subquery, Value, Exists
from django.db.models.functions import Coalesce
from django.shortcuts import render
from .models import Department, Student, Advisor, Supervisor, Company, Internship, Notification, User, DepartmentHead

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    active_section = request.GET.get('section', 'admin_dashboard')
    user_filter = request.GET.get('filter', None)

    # Total counts
    total_departments = Department.objects.count()
    total_students = Student.objects.count()
    total_advisors = Advisor.objects.count()
    total_supervisors = Supervisor.objects.count()
    total_companies = Company.objects.count()
    total_internships = Internship.objects.count()
    total_notifications = Notification.objects.count()
    total_users = User.objects.count()
    active_internships = Internship.objects.filter(is_open=True).count()

    # Default recent users
    recent_users = User.objects.order_by('username')[:1000]

    # Role-specific user filters
    if user_filter == 'students':
        recent_users = User.objects.filter(is_student=True).order_by('username')[:100]
    elif user_filter == 'advisors':
        recent_users = User.objects.filter(is_advisor=True).order_by('username')[:100]
    elif user_filter == 'department_heads':
        recent_users = User.objects.filter(is_department_head=True).order_by('username')[:100]
    elif user_filter == 'company_admins':
        recent_users = User.objects.filter(is_company_admin=True).order_by('username')[:100]
    elif user_filter == 'supervisors':
        recent_users = User.objects.filter(is_supervisor=True).order_by('username')[:100]

    # Role-specific counts
    student_count = User.objects.filter(is_student=True).count()
    advisor_count = User.objects.filter(is_advisor=True).count()
    supervisor_count = User.objects.filter(is_supervisor=True).count()
    company_admin_count = User.objects.filter(is_company_admin=True).count()
    department_head_count = User.objects.filter(is_department_head=True).count()

    # Additional statistics
    students_with_internships = Student.objects.filter(internship__isnull=False).distinct().count()
    avg_students_per_advisor = Advisor.objects.annotate(
        student_count=Count('student')
    ).aggregate(avg=Avg('student_count'))['avg'] or 0

    supervising_internships = Student.objects.filter(
        assigned_supervisor__isnull=False,
        internship__isnull=False
    ).count()

    departments_managed = DepartmentHead.objects.count()
    logged_in_user = request.user
    managing_companies = Company.objects.filter(companyadmin__isnull=False).count()

    # Department stats
    departments_with_heads_count = Department.objects.annotate(
        has_head=Exists(DepartmentHead.objects.filter(department=OuterRef('pk')))
    ).filter(has_head=True).count()

    avg_students_per_dept = Department.objects.annotate(
        student_count=Count('student')
    ).aggregate(avg=Avg('student_count'))['avg'] or 0

    # Departments data with head names
    departments = Department.objects.annotate(
        student_count=Count('student'),
        head_name=Coalesce(
            Subquery(
                DepartmentHead.objects.filter(department=OuterRef('pk')).values('user__username')[:1]
            ),
            Value('Not assigned')
        )
    ).order_by('name')

    # Companies data with internship counts
    companies = Company.objects.annotate(
        internship_count=Count('internship')
    ).order_by('name')

    context = {
        'logged_in_user': logged_in_user,
        'active_section': active_section,
        'current_filter': user_filter,
        'total_departments': total_departments,
        'total_students': total_students,
        'total_advisors': total_advisors,
        'total_supervisors': total_supervisors,
        'total_companies': total_companies,
        'total_internships': total_internships,
        'total_notifications': total_notifications,
        'total_users': total_users,
        'recent_users': recent_users,
        'active_internships': active_internships,
        'departments': departments,
        'companies': companies,
        'student_count': student_count,
        'advisor_count': advisor_count,
        'supervisor_count': supervisor_count,
        'company_admin_count': company_admin_count,
        'department_head_count': department_head_count,
        'students_with_internships': students_with_internships,
        'avg_students_per_advisor': avg_students_per_advisor,
        'supervising_internships': supervising_internships,
        'departments_managed': departments_managed,
        'managing_companies': managing_companies,
        'departments_with_heads_count': departments_with_heads_count,
        'avg_students_per_dept': avg_students_per_dept,
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
    user = request.user

    # Check if user is a department head
    if hasattr(user, 'departmenthead'):
        department = user.departmenthead.department
    else:
        return redirect('unauthorized')  # Redirect if not authorized

    # Get students in the department
    students = Student.objects.filter(department=department)

    # Approved applications from these students
    approved_applications = Application.objects.filter(
        student__in=students,
        status='approved'
    )

    # Count applications by student
    student_names = []
    student_application_counts = []
    for student in students:
        count = approved_applications.filter(student=student).count()
        if count > 0:
            student_names.append(f"{student.user.first_name} {student.user.last_name}")
            student_application_counts.append(count)

    # Companies offering internships that received applications from these students
    companies = Company.objects.all()
    company_names = []
    internships_offered = []
    applications_received = []

    for company in companies:
        # Internships posted by this company
        internships = Internship.objects.filter(company=company)
        
        # Applications by department students for this company's internships
        apps = Application.objects.filter(
            internship__in=internships,
            student__in=students
        )

        company_names.append(company.name)
        internships_offered.append(internships.count())
        applications_received.append(apps.count())

    context = {
        'companies': companies,
        'company_names': company_names,
        'internships_offered': internships_offered,
        'applications_received': applications_received,
        'company_feedbacks': CompanyFeedback.objects.all(),
        'student_names': student_names,
        'student_application_counts': student_application_counts,
    }
    return render(request, 'company/company_management.html', context)
@login_required
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company added successfully!')
            return redirect('admin_dashboard')
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
            return redirect('company_admin_dashboard')
        else:
            print("Form Errors:", form.errors)  # Debugging: Print errors to console/log
    else:
        form = CompanyForm(instance=company)
    
    return render(request, 'company/edit_company.html', {'form': form, 'company': company})



@login_required
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, 'Company deleted successfully!')
    return redirect('company_management')
def is_department_head(user):
    return user.is_authenticated and hasattr(user, 'is_department_head') and user.is_department_head
from django.db.models import Count, Q
@login_required
@user_passes_test(is_department_head)
def view_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    department = request.user.departmenthead.department  # assuming dept head is linked to department

    # Filter internships for the company
    internships = Internship.objects.filter(company=company)

    # Annotate each internship with number of approved applications from the same department
    internships = internships.annotate(
        approved_applications=Count(
            'application',
            filter=Q(application__status='Approved') & Q(application__student__department=department)
        )
    )

    feedbacks = CompanyFeedback.objects.filter(company=company)

    context = {
        'company': company,
        'internships': internships,
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
@user_passes_test(lambda u: u.is_department_head)
def student_management(request):
    # Get the department of the logged-in department head
    department_head = DepartmentHead.objects.get(user=request.user)
    department = department_head.department

    # Filter students by the department
    students = Student.objects.filter(department=department)

    # Identify students with approved applications
    students_with_approved_applications = []
    for student in students:
        if student.application_set.filter(status='Approved').exists():
            students_with_approved_applications.append(student)

    # Pass the students and the list of students with approved applications to the template
    return render(request, 'students/student_management.html', {
        'students': students,
        'students_with_approved_applications': students_with_approved_applications
    })

@login_required
@user_passes_test(lambda u: u.is_supervisor)
def monthly_evaluation(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = MonthlyEvaluationForm(request.POST)
        if form.is_valid():
            # Save to database
            evaluation = form.save(commit=False)
            evaluation.student = student
            evaluation.supervisor = request.user.supervisor
            evaluation.save()
            
            # Generate PDF (your existing code)
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer)
            
            # University Header
            pdf.drawString(100, 800, "ADDIS ABABA SCIENCE AND TECHNOLOGY UNIVERSITY")
            pdf.drawString(100, 780, "INTERNSHIP INDUSTRY SUPERVISOR MONTHLY PERFORMANCE EVALUATION FORMAT")
            
            # Student/Supervisor Info
            pdf.drawString(100, 760, f"Month: {form.cleaned_data['month']}")
            pdf.drawString(100, 740, f"Company Name: {student.internship.company.name}")
            pdf.drawString(100, 720, f"Supervisor's Name: {request.user.get_full_name()}")
            pdf.drawString(100, 700, f"Supervisor's Phone No.: {request.user.phone}")
            pdf.drawString(100, 680, f"Student's Full Name: {student.user.get_full_name()}")
            pdf.drawString(100, 660, f"Student's ID No.: {student.user.username}")
            pdf.drawString(100, 640, f"Student's Department: {student.department.name}")
            
            # Evaluation Sections (same as your template)
            pdf.drawString(100, 620, "General Performance (25%)")
            pdf.drawString(120, 600, f"Punctuality (5%): {form.cleaned_data['punctuality']}")
            # ... [Include all other sections from your original PDF code] ...
            
            pdf.save()
            buffer.seek(0)
            
            # Return PDF for download
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="monthly_evaluation_{student.user.username}.pdf"'
            return response
    else:
        # Auto-fill form with student/supervisor data
        initial_data = {
            'month': timezone.now().strftime("%B %Y"),
            'company_name': student.internship.company.name,
            'supervisor_name': request.user.get_full_name(),
            'supervisor_phone': request.user.phone,
            'student_name': student.user.get_full_name(),
            'student_id': student.user.username,
            'student_department': student.department.name
        }
        form = MonthlyEvaluationForm(initial=initial_data)
    
    return render(request, 'supervisors/monthly_evaluation.html', {
        'form': form,
        'student': student,
        'reports': DailyWorkReportForm.objects.filter(student=student).order_by('-work_date')[:28]  # Last 4 weeks
    })

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
# views.py
@login_required
@user_passes_test(lambda u: u.is_department_head)
def view_monthly_evaluation(request, evaluation_id):
    evaluation = get_object_or_404(MonthlyEvaluation, id=evaluation_id)
    
    # Verify department head has access
    if evaluation.student.department != request.user.departmenthead.department:
        raise PermissionDenied()

    # Generate PDF (using your existing code)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    
    # Header
    pdf.drawString(100, 800, "ADDIS ABABA SCIENCE AND TECHNOLOGY UNIVERSITY")
    pdf.drawString(100, 780, "MONTHLY PERFORMANCE EVALUATION")
    
    # Student Info
    pdf.drawString(100, 760, f"Month: {evaluation.month}")
    pdf.drawString(100, 740, f"Student: {evaluation.student.user.get_full_name()}")
    
    # Evaluation Data
    pdf.drawString(100, 720, "General Performance (25%)")
    pdf.drawString(120, 700, f"Punctuality: {evaluation.punctuality}/5")
    # ... [include all evaluation fields] ...
    
    pdf.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Avg

@login_required
@user_passes_test(lambda u: u.is_department_head)
def view_student_progress(request, user_id):
    student = get_object_or_404(Student, user__id=user_id)
    department_head = request.user.departmenthead
    application = student.application_set.filter(status='Approved').first()
    if not application:
        messages.error(request, "You must have an approved internship application.")
        return redirect('student_dashboard')

    internship = application.internship
    # Ensure student belongs to the same department
    if student.department != department_head.department:
        raise PermissionDenied("You can only view students from your department.")

    # Task data
    tasks = Task.objects.filter(student=student).order_by('work_date')
    internship_months = int(internship.duration)

    # Get workdays_per_week before using it
    schedule = WorkSchedule.objects.filter(student=student, is_active=True).first()
    workdays_per_week = schedule.workdays_per_week if schedule else 5

    completed_tasks = internship_months * 4 * workdays_per_week
    pending_tasks = tasks.filter(status='pending').count()

    # Group tasks by week
    grouped_tasks = []
    weekly_tasks = []
    week_number = 1

    for task in tasks:
        weekly_tasks.append(task)
        if len(weekly_tasks) == workdays_per_week:
            grouped_tasks.append({
                'week_number': week_number,
                'tasks': weekly_tasks,
                'week_start': weekly_tasks[0].work_date,
                'is_complete': all(t.status == 'completed' for t in weekly_tasks)
            })
            weekly_tasks = []
            week_number += 1

    if weekly_tasks:
        grouped_tasks.append({
            'week_number': week_number,
            'tasks': weekly_tasks,
            'week_start': weekly_tasks[0].work_date,
            'is_complete': False
        })

    # Monthly Evaluations
    evaluations = MonthlyEvaluation.objects.filter(student=student).order_by('created_at')
    evaluations_count = evaluations.count()

    if evaluations_count > 0:
        average_score = evaluations.aggregate(Avg('total_score'))['total_score__avg']
        avg_punctuality = evaluations.aggregate(Avg('punctuality'))['punctuality__avg']
        avg_reliability = evaluations.aggregate(Avg('reliability'))['reliability__avg']
        avg_communication = evaluations.aggregate(Avg('communication'))['communication__avg']
        avg_technical_skills = evaluations.aggregate(Avg('technical_skills'))['technical_skills__avg']
        avg_responsibility = evaluations.aggregate(Avg('responsibility'))['responsibility__avg'] / 3
        avg_teamwork = evaluations.aggregate(Avg('team_quality'))['team_quality__avg'] / 4
        evaluation_dates = [e.month for e in evaluations]
        evaluation_scores = [e.total_score for e in evaluations]
    else:
        average_score = 0
        avg_punctuality = avg_reliability = avg_communication = 0
        avg_technical_skills = avg_responsibility = avg_teamwork = 0
        evaluation_dates = []
        evaluation_scores = []

    # Final Evaluation (Supervisor Evaluation)
    # Get internship either from student or approved application
    internship = student.internship
    if not internship:
        approved_app = Application.objects.filter(student=student, status='Approved').first()
        internship = approved_app.internship if approved_app else None

    final_evaluation = Evaluation.objects.filter(internship=internship).first() if internship else None

    context = {
        'student': student,
        'monthly_evaluations': evaluations,
        'evaluations_count': evaluations_count,
        'average_score': average_score,
        'evaluation_dates': evaluation_dates,
        'evaluation_scores': evaluation_scores,
        'avg_punctuality': avg_punctuality or 0,
        'avg_reliability': avg_reliability or 0,
        'avg_communication': avg_communication or 0,
        'avg_technical_skills': avg_technical_skills or 0,
        'avg_responsibility': avg_responsibility or 0,
        'avg_teamwork': avg_teamwork or 0,
        'grouped_tasks': grouped_tasks,
        'workdays_per_week': workdays_per_week,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'all_tasks': tasks,
        'final_evaluation': final_evaluation,  
    }

    return render(request, 'students/view_student_progress.html', context)

@login_required
def add_student(request):
    user = request.user

    # Determine base template based on user role
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_department_head", False):
        base_template = "departement_head/base.html"
    elif getattr(user, "is_advisor", False):
        base_template = "advisors/base.html"
    elif getattr(user, "is_supervisor", False):
        base_template = "supervisor/base.html"
    elif getattr(user, "is_student", False):
        base_template = "students/base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        base_template = "base.html"  # Default fallback

    # Superadmin case
    if user.is_superuser:
        if request.method == 'POST':
            form = SuperadminStudentForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Student registered successfully!')
                return redirect('admin_dashboard')
        else:
            form = SuperadminStudentForm()

    # Department Head case
    elif getattr(user, "is_department_head", False):
        department = user.departmenthead.department
        if request.method == 'POST':
            form = DepartmentHeadStudentForm(
                request.POST, request.FILES, department=department
            )
            if form.is_valid():
                form.save()
                messages.success(request, 'Student registered successfully!')
                return redirect('student_management')
        else:
            form = DepartmentHeadStudentForm(department=department)

    # Unauthorized access
    else:
        return redirect('unauthorized_access')

    return render(request, 'students/add_student.html', {
        'form': form,
        'is_superuser': user.is_superuser,
        'base_template': base_template
    })

@login_required
def view_student(request, student_id):
    student = get_object_or_404(Student, user_id=student_id)
    return render(request, 'students/view_student.html', {'student': student})
@login_required
def student_activity(request, student_id):
    # Ensure the user is a supervisor
    if not request.user.is_supervisor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('supervisor_dashboard')

    # Get the student
    student = get_object_or_404(Student, user_id=student_id)

    # Debug: Print the student's details
    print(f"Student: {student.user.get_full_name()} (ID: {student.user.id})")

    # Get tasks assigned to the student
    tasks = Task.objects.filter(student=student).order_by('created_at')

    # Debug: Print the tasks queryset
    print(f"Tasks for {student.user.get_full_name()}: {tasks}")

    return render(request, 'supervisor/student_activity.html', {
        'student': student,
        'tasks': tasks,
    })
@login_required
@user_passes_test(lambda u: u.is_department_head)
def edit_student(request, student_user_id):
    student = get_object_or_404(Student, user_id=student_user_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_management')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/edit_student.html', {'form': form, 'student': student})

@login_required
def delete_student(request, student_user_id):
    student = get_object_or_404(Student, user_id=student_user_id)
    student.delete()
    return redirect('student_management')
# views.py
@login_required
def student_dashboard(request):
    student = request.user.student  # Get the student object

    # Fetch the approved application (if any)
    approved_application = Application.objects.filter(
        student=student, 
        status='Approved'
    ).first()

    # Check if the student has permission to create chat groups
   

    return render(request, 'students/student_dashboard.html', {
        'approved_application': approved_application,
        'student': student,  # Pass the student object to the template
        'user': request.user,  # Ensure user is passed
        
    })
@login_required
def department_head_dashboard(request):
    user = request.user
    department_head = get_object_or_404(DepartmentHead, user=user)
    department = department_head.department

    # Student statistics for the department
    students = Student.objects.filter(department=department)
    student_count = students.count()
    
    # Student status counts
    student_active_count = students.filter(status='active').count()
    student_inactive_count = students.filter(status='inactive').count()
    
    # Students with different internship statuses
    internship_approved_students = students.filter(
        application__status='approved'
    ).distinct().count()
    
    internship_pending_students = students.filter(
        application__status='pending'
    ).distinct().count()
    
    internship_rejected_students = students.filter(
        application__status='rejected'
    ).distinct().count()

    # Internship applications statistics for department students
    department_applications = Application.objects.filter(
        student__department=department
    )
    internship_approved_count = department_applications.filter(status='approved').count()
    internship_pending_count = department_applications.filter(status='pending').count()
    internship_rejected_count = department_applications.filter(status='rejected').count()

    # Get all unique industry names and counts from the database
    industries = Company.objects.values('industry').annotate(
        count=Count('industry')
    ).order_by('-count')

    context = {
        'user': user,
        'department': department,
        'student_count': student_count,
        'student_active_count': student_active_count,
        'student_inactive_count': student_inactive_count,
        
        # Students with different internship statuses
        'student_internship_approved_count': internship_approved_students,
        'student_internship_pending_count': internship_pending_students,
        'student_internship_rejected_count': internship_rejected_students,
        
        # Application status counts
        'internship_approved_count': internship_approved_count,
        'internship_pending_count': internship_pending_count,
        'internship_rejected_count': internship_rejected_count,
        
        'total_companies': Company.objects.count(),
        'total_internships': Internship.objects.count(),
        'advisor_count': Advisor.objects.filter(department=department).count(),
        'industry_labels': [item['industry'] for item in industries if item['industry']],
        'industry_counts': [item['count'] for item in industries if item['industry']],
    }
    return render(request, 'departement_head/department_head_dashboard.html', context)

@login_required
def industry_supervisor_dashboard(request):
    return render(request, 'supervisor/industry_supervisor_dashboard.html', {'user': request.user})
from django.contrib.auth import get_user_model
User = get_user_model()
def advisor_dashboard(request):
    # Ensure the logged-in user is an advisor
    advisor = Advisor.objects.filter(user=request.user).first()

    if not advisor:
        print("DEBUG: No Advisor found for user:", request.user)  # Debugging output

    context = {"advisor": advisor}
    return render(request, "advisors/advisor_dashboard.html", context)

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
@login_required
def supervisor_register(request):
    user = request.user

    # Base template logic (optional for layout)
    if user.is_superuser:
        base_template = "admin/admin_base.html"
    elif getattr(user, "is_company_admin", False):
        base_template = "Company_Admin/base.html"
    else:
        return redirect('unauthorized_access')

    # Superadmin case
    if user.is_superuser:
        if request.method == 'POST':
            form = SuperadminSupervisorForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Supervisor registered successfully!')
                return redirect('admin_dashboard')
        else:
            form = SuperadminSupervisorForm()

    # CompanyAdmin case
    elif hasattr(user, 'companyadmin'):
        company_admin = user.companyadmin
        if request.method == 'POST':
            form = CompanyAdminSupervisorForm(request.POST, request.FILES, company_admin=company_admin)
            if form.is_valid():
                form.save()
                messages.success(request, 'Supervisor registered successfully!')
                return redirect('supervisor_list')
        else:
            form = CompanyAdminSupervisorForm(company_admin=company_admin)

    return render(request, 'supervisor/supervisor_register.html', {
        'form': form,
        'base_template': base_template,
        'is_superuser': user.is_superuser
    })
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def supervisor_list(request):
    # Get the company of the logged-in company admin
    company_admin = get_object_or_404(CompanyAdmin, user=request.user)
    company = company_admin.company

    # Get the supervisors belonging to the company
    supervisors = Supervisor.objects.filter(company=company)

    # Pass the data to the template
    return render(request, 'supervisor/supervisor_list.html', {
        'supervisors': supervisors,
        'company': company,
    })
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def view_supervisor_details(request, supervisor_id):
    # Get the supervisor
    supervisor = get_object_or_404(Supervisor, user_id=supervisor_id)
    
    # Pass the supervisor to the template
    return render(request, 'supervisor/view_supervisor_details.html', {
        'supervisor': supervisor,
    })
# views.py
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def update_supervisor(request, supervisor_id):
    company_admin = get_object_or_404(CompanyAdmin, user=request.user)
    supervisor = get_object_or_404(Supervisor, user_id=supervisor_id, company=company_admin.company)
    
    if request.method == 'POST':
        form = SupervisorForm(request.POST, instance=supervisor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supervisor updated successfully!')
            return redirect('supervisor_list')
    else:
        form = SupervisorForm(instance=supervisor)
    
    return render(request, 'supervisor/update_supervisor.html', {
        'form': form,
        'supervisor': supervisor,
    })
@login_required
@user_passes_test(lambda u: u.is_company_admin)
def delete_supervisor(request, supervisor_id):
    # Get the logged-in company admin
    company_admin = get_object_or_404(CompanyAdmin, user=request.user)
    
    # Get the supervisor (ensure they belong to the company admin's company)
    supervisor = get_object_or_404(Supervisor, user_id=supervisor_id, company=company_admin.company)
    
    # Delete the supervisor
    supervisor.user.delete()  # Delete the associated user
    messages.success(request, f"Supervisor {supervisor.user.get_full_name()} deleted successfully!")
    
    return redirect('supervisor_list')
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

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer

def notify_department_head(self, evaluation):
    """Notify the student's department head about the evaluation"""
    department_head = DepartmentHead.objects.filter(
        department=evaluation.student.department
    ).first()
    
    if department_head:
        message = (
            f"New monthly evaluation for {evaluation.student.user.get_full_name()} "
            f"({evaluation.month}) with score: {evaluation.total_score()}/100"
        )
        
        Notification.objects.create(
            user=department_head.user,
            message=message,
            link=f"/students/{evaluation.student.pk}/evaluations/"
        )
# views.py
@login_required
def view_student_evaluations(request, student_id):
    if not hasattr(request.user, 'departmenthead'):
        messages.error(request, "Only department heads can access this page")
        return redirect('dashboard')
    
    department_head = request.user.departmenthead
    student = get_object_or_404(Student, pk=student_id)
    
    # Verify student is in department head's department
    if student.department != department_head.department:
        messages.error(request, "This student is not in your department")
        return redirect('department_head_dashboard')
    
    evaluations = MonthlyEvaluation.objects.filter(
        student=student
    ).order_by('-created_at')
    
    context = {
        'student': student,
        'evaluations': evaluations,
    }
    return render(request, 'department_head/student_evaluations.html', context)

from datetime import timedelta
def weekly_tasks_view(request, student_id):
    # Fetch the student and their work schedule
    student = get_object_or_404(Student, id=student_id)
    work_schedule = WorkSchedule.objects.get(student=student)
    
    # Calculate the start date of the current week (example: Monday as the start of the week)
    today = timezone.now().date()
    week_start_date = today - timedelta(days=today.weekday())  # Monday as the start of the week
    
    # Fetch tasks for the current week
    tasks = Task.objects.filter(student=student, work_date__gte=week_start_date, work_date__lt=week_start_date + timedelta(days=7))
    
    # Determine the week number (example: week number since the start of the program)
    week_number = (today - work_schedule.start_date).days // 7 + 1
    
    context = {
        'student': student,
        'work_schedule': work_schedule,
        'tasks': tasks,
        'week_start_date': week_start_date,
        'week': week_number,
    }
    return render(request, 'supervisor/provide_weekly_feedback.html', context)
@user_passes_test(lambda u: u.is_student)
def view_tasks(request):
    student = get_object_or_404(Student, user=request.user)
    tasks = Task.objects.filter(student=student).order_by('-created_at')
    return render(request, 'students/view_tasks.html', {'tasks': tasks})
@login_required
def edit_task(request, task_id):
    task = Task.objects.get(id=task_id, student=request.user.student)
    
    if not task.can_edit_or_delete():
        messages.error(request, "You can only edit a task within 24 hours of submission.")
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = DailyTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('student_dashboard')
    else:
        form = DailyTaskForm(instance=task)

    return render(request, 'students/edit_task.html', {'form': form})

@login_required
def delete_task(request, task_id):
    task = Task.objects.get(id=task_id, student=request.user.student)
    
    if not task.can_edit_or_delete():
        messages.error(request, "You can only delete a task within 24 hours of submission.")
        return redirect('student_dashboard')

    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect('student_dashboard')

# Student Views
def submit_task(request):
    student = request.user.student
    schedule = WorkSchedule.objects.get(student=student)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if timezone.now().date() in schedule.get_work_dates():
                task.student = student
                task.save()
                return redirect('student_dashboard')

@login_required
@user_passes_test(lambda u: u.is_supervisor)
def assign_workdays(request):
    if request.method == 'POST':
        days = request.POST.get('workdays_per_week')
        if not days:
            messages.error(request, "Missing required 'workdays_per_week' parameter")
            return redirect('assigned_students')
        try:
            days = int(days)
        except ValueError:
            messages.error(request, "Invalid value for workdays")
            return redirect('assigned_students')

        supervisor = request.user.supervisor
        assigned_students = Student.objects.filter(assigned_supervisor=supervisor)

        updated = 0
        for student in assigned_students:
            schedule, created = WorkSchedule.objects.get_or_create(
                student=student,
                defaults={'supervisor': supervisor}
            )
            schedule.supervisor = supervisor  # Ensure supervisor is set
            schedule.workdays_per_week = days
            schedule.save()
            updated += 1

        messages.success(request, f"Work schedule updated for {updated} students")
        return redirect('assigned_students')

    return redirect('assigned_students')
@login_required
@user_passes_test(lambda u: u.is_student)
def submit_daily_task(request):
    student = request.user.student
    today = now().date()

    application = Application.objects.filter(student=student, status='Approved').first()
    if not application:
        messages.error(request, "You must have an approved internship application to submit tasks.")
        return redirect('student_dashboard')

    internship = application.internship

    # ❗️ Check if final evaluation is already submitted
    if Evaluation.objects.filter(internship=internship).exists():
        messages.error(request, "You cannot submit tasks after your final evaluation has been submitted.")
        return redirect('student_dashboard')

    try:
        work_schedule = WorkSchedule.objects.get(student=student, is_active=True)
    except WorkSchedule.DoesNotExist:
        messages.error(request, "No active work schedule assigned.")
        return redirect('student_dashboard')

    internship_months = int(internship.duration)
    workdays_per_week = work_schedule.workdays_per_week
    max_allowed_reports = internship_months * 4 * workdays_per_week

    submitted_reports_count = Task.objects.filter(
        student=student,
        status__in=['pending', 'completed']
    ).count()

    duration_valid = submitted_reports_count < max_allowed_reports

    # Only allow editing if 'edit' query param is passed
    edit_requested = request.GET.get('edit') == '1'
    existing_task = Task.objects.filter(student=student, work_date=today).first() if edit_requested else None
    is_edit = existing_task is not None

    if not is_edit and not duration_valid:
        return render(request, 'students/submit_daily_task.html', {
            'duration_valid': False,
            'is_edit': False,
            'today': today,
        })

    if request.method == 'POST':
        form = DailyTaskForm(request.POST, instance=existing_task)
        if form.is_valid():
            task = form.save(commit=False)
            task.student = student
            task.work_date = today
            task.internship = internship
            task.supervisor = student.assigned_supervisor
            task.status = 'pending' if 'save' in request.POST else 'completed'
            task.save()

            messages.success(
                request,
                "Task updated!" if is_edit else "Task submitted successfully!"
            )
            return redirect('view_submitted_tasks')
    else:
        form = DailyTaskForm(instance=existing_task)

    return render(request, 'students/submit_daily_task.html', {
        'form': form,
        'today': today,
        'is_edit': is_edit,
        'duration_valid': duration_valid,
    })

@login_required
@user_passes_test(lambda u: u.is_supervisor)
def submit_monthly_evaluation(request, student_id, month_number):
    student = get_object_or_404(Student, user_id=student_id)
    supervisor = request.user.supervisor

    if student.assigned_supervisor != supervisor:
        raise PermissionDenied("You are not assigned to this student")

    # Get all feedbacks (optional use only)
    all_feedbacks = WeeklyFeedback.objects.filter(student=student).order_by('id')
    start_index = (month_number - 1) * 4
    end_index = start_index + 4
    month_feedbacks = all_feedbacks[start_index:end_index]

    # Create or get evaluation
    evaluation, created = MonthlyEvaluation.objects.get_or_create(
        student=student,
        month_number=month_number,
        defaults={
            'supervisor': supervisor,
            'month': f"Month {month_number}"
        }
    )

    if request.method == 'POST':
        form = MonthlyEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.supervisor = supervisor
            evaluation.total_score = evaluation.calculate_total_score()
            evaluation.save()
            messages.success(request, f"Evaluation for Month {month_number} submitted successfully!")
            return redirect('student_reported_tasks', student_id=student.user_id)
    else:
        # Optional: Pre-fill from averages if feedbacks exist
        if month_feedbacks.exists():
            avg_fields = ['punctuality', 'reliability', 'communication', 'engagement']
            avg_values = {
                field: month_feedbacks.aggregate(Avg(field))[f'{field}__avg'] or 0
                for field in avg_fields
            }
            initial_data = {k: round(v) for k, v in avg_values.items()}
        else:
            initial_data = {}
        form = MonthlyEvaluationForm(instance=evaluation, initial=initial_data)

    context = {
        'student': student,
        'form': form,
        'weekly_reports': month_feedbacks,  # Can be empty now
        'month_name': f"Month {month_number}",
        'month_number': month_number,
        'progress': evaluation.get_category_progress() if not created else None,
    }
    return render(request, 'Supervisor/submit_monthly_evaluation.html', context)

def edit_monthly_evaluation(request, student_id, month_number):
    evaluation = get_object_or_404(MonthlyEvaluation, student_id=student_id, month_number=month_number)

    if request.method == 'POST':
        form = MonthlyEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            return redirect('student_progress_view', student_id=student_id)
    else:
        form = MonthlyEvaluationForm(instance=evaluation)

    return render(request, 'Supervisor/edit_monthly_evaluation.html', {
        'form': form,
        'student_id': student_id,
        'month_number': month_number,
    })
@login_required
def view_submitted_tasks(request):
    if not request.user.is_student:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('student_dashboard')

    student = request.user.student
    schedule = WorkSchedule.objects.filter(student=student, is_active=True).first()

    if not schedule:
        messages.warning(request, "No active work schedule found")
        return redirect('student_dashboard')

    today = now().date()

    # Get approved internship application
    application = student.application_set.filter(status='Approved').first()
    if not application:
        messages.error(request, "You must have an approved internship application.")
        return redirect('student_dashboard')

    internship = application.internship

    # Determine if student can rate the company
    can_rate_company = False
    if internship:
        # Final evaluation exists if an Evaluation object for this internship exists
        final_evaluation_exists = Evaluation.objects.filter(internship=internship).exists()

        # Check if the student has already rated this internship
        has_already_rated = CompanyRating.objects.filter(student=student, internship=internship).exists()

        can_rate_company = final_evaluation_exists and not has_already_rated

    # Organize tasks
    tasks = Task.objects.filter(student=student).select_related('supervisor').order_by('work_date')
    workdays_per_week = schedule.workdays_per_week
    internship_months = int(internship.duration)

    max_allowed_reports = internship_months * 4 * workdays_per_week
    submitted_reports_count = tasks.filter(status__in=['pending', 'completed']).count()
    duration_valid = submitted_reports_count < max_allowed_reports

    # Group tasks by week
    grouped_tasks = []
    weekly_tasks = []
    for index, task in enumerate(tasks):
        weekly_tasks.append(task)
        if (index + 1) % workdays_per_week == 0:
            grouped_tasks.append({
                'week_number': len(grouped_tasks) + 1,
                'tasks': weekly_tasks,
                'week_start': weekly_tasks[0].work_date
            })
            weekly_tasks = []

    if weekly_tasks:
        grouped_tasks.append({
            'week_number': len(grouped_tasks) + 1,
            'tasks': weekly_tasks,
            'week_start': weekly_tasks[0].work_date
        })

    context = {
        'grouped_tasks': grouped_tasks,
        'workdays_per_week': workdays_per_week,
        'schedule': schedule,
        'today': today,
        'duration_valid': duration_valid,
        'can_rate_company': can_rate_company,
        'internship': internship,
    }

    return render(request, 'students/view_submitted_tasks.html', context)

def student_progress_view(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    schedule = WorkSchedule.objects.filter(student=student, is_active=True).first()

    if not schedule:
        return redirect('view_student_progress', student_id=student_id)

    tasks = student.tasks.all().order_by('work_date')
    workdays_per_week = schedule.workdays_per_week

    # Get internship from student or approved application
    internship = student.internship
    if not internship:
        approved_app = Application.objects.filter(student=student, status='Approved').first()
        internship = approved_app.internship if approved_app else None

    # Safely calculate required tasks
    try:
        duration_months = int(internship.duration) if internship else 0
    except (AttributeError, ValueError):
        duration_months = 0

    required_tasks = workdays_per_week * 4 * duration_months
    completed_tasks = tasks.count()

    can_submit_final = internship and completed_tasks >= required_tasks
    existing_evaluation = Evaluation.objects.filter(internship=internship).exists() if internship else False

    # Group tasks by week
    grouped_tasks = []
    weekly_tasks = []
    week_number = 1

    for i, task in enumerate(tasks):
        weekly_tasks.append(task)
        if len(weekly_tasks) == workdays_per_week:
            all_have_feedback = all(t.supervisor_feedback for t in weekly_tasks)
            month_number = (week_number - 1) // 4 + 1
            month_evaluation_exists = MonthlyEvaluation.objects.filter(student=student, month_number=month_number).exists()

            grouped_tasks.append({
                'week_number': week_number,
                'tasks': weekly_tasks,
                'is_complete': True,
                'has_feedback': all_have_feedback,
                'month_evaluation_exists': month_evaluation_exists,
            })
            weekly_tasks = []
            week_number += 1

    if weekly_tasks:
        all_have_feedback = all(t.supervisor_feedback for t in weekly_tasks)
        month_number = (week_number - 1) // 4 + 1
        month_evaluation_exists = MonthlyEvaluation.objects.filter(student=student, month_number=month_number).exists()

        grouped_tasks.append({
            'week_number': week_number,
            'tasks': weekly_tasks,
            'is_complete': False,
            'has_feedback': all_have_feedback,
            'month_evaluation_exists': month_evaluation_exists,
        })

    context = {
        'student': student,
        'work_schedule': schedule,
        'grouped_tasks': grouped_tasks,
        'can_submit_final': can_submit_final and not existing_evaluation,
        'existing_evaluation': existing_evaluation,
        'completed_tasks': completed_tasks,
        'required_tasks': required_tasks,
    }

    return render(request, 'Supervisor/student_reported_tasks.html', context)



def provide_weekly_feedback(request, student_id, week_number):
    student = get_object_or_404(Student, user_id=student_id)
    schedule = get_object_or_404(WorkSchedule, student=student, is_active=True)
    
    # Get tasks for the week
    start_index = (week_number - 1) * schedule.workdays_per_week
    end_index = start_index + schedule.workdays_per_week
    tasks = student.tasks.all().order_by('work_date')[start_index:end_index]
    
    if request.method == 'POST':
        form = TaskFeedbackForm(request.POST)
        if form.is_valid():
            # Save feedback for all tasks in the week
            for task in tasks:
                task.supervisor_feedback = form.cleaned_data['supervisor_feedback']
                task.save()
            return redirect('student_reported_tasks', student_id=student_id)
    else:
        form = TaskFeedbackForm()
    
    context = {
        'student': student,
        'week_number': week_number,
        'tasks': tasks,
        'form': form
    }
    return render(request,'Supervisor/provide_weekly_feedback.html', context)
def edit_weekly_feedback(request, student_id, week_number):
    student = get_object_or_404(Student, user_id=student_id)
    schedule = get_object_or_404(WorkSchedule, student=student, is_active=True)

    # Get all tasks for the specified week
    start_index = (week_number - 1) * schedule.workdays_per_week
    end_index = start_index + schedule.workdays_per_week
    tasks = student.tasks.all().order_by('work_date')[start_index:end_index]

    if not tasks.exists():
        return HttpResponse("No tasks found for this week.", status=404)

    # Use first task's feedback as initial data
    initial_feedback = tasks.first().supervisor_feedback if tasks.first().supervisor_feedback else ''

    if request.method == 'POST':
        form = TaskFeedbackForm(request.POST)
        if form.is_valid():
            # Update feedback on all tasks
            for task in tasks:
                task.supervisor_feedback = form.cleaned_data['supervisor_feedback']
                task.save()
            return redirect('student_reported_tasks', student_id=student_id)
    else:
        form = TaskFeedbackForm(initial={'supervisor_feedback': initial_feedback})

    context = {
        'student': student,
        'week_number': week_number,
        'tasks': tasks,
        'form': form
    }
    return render(request, 'Supervisor/edit_weekly_feedback.html', context)
@login_required
def supervisor_feedback_view(request):
    # Ensure the logged-in user is a supervisor
    if not request.user.is_supervisor:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('supervisor_dashboard')

    # Get the supervisor instance for the logged-in user
    supervisor = request.user.supervisor

    # Get the current week's start date (Monday)
    today = timezone.now().date()
    week_start_date = today - timedelta(days=today.weekday())

    # Fetch tasks for the current week for all students assigned to this supervisor
    tasks = Task.objects.filter(
        student__workschedule__supervisor=supervisor,
        work_date__gte=week_start_date,
        work_date__lt=week_start_date + timedelta(days=7)
    ).order_by('work_date')

    # Handle feedback submission
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        if feedback_text and feedback_text.strip():  # Ensure feedback is not empty
            # Get the first student assigned to the supervisor
            work_schedule = WorkSchedule.objects.filter(
                supervisor=supervisor
            ).first()

            if work_schedule:
                # Create or update weekly feedback
                WeeklyFeedback.objects.create(
                    student=work_schedule.student,
                    supervisor=supervisor,
                    week_start_date=week_start_date,
                    comments=feedback_text
                )
                messages.success(request, "Weekly feedback submitted successfully!")
            else:
                messages.error(request, "No student work schedule found for this supervisor.")
        else:
            messages.error(request, "Feedback cannot be empty.")
        return redirect('supervisor_feedback')

    return render(request, 'supervisor/supervisor_feedback.html', {
        'tasks': tasks,
        'week_start_date': week_start_date
    })
@login_required
@user_passes_test(lambda u: u.is_advisor)
def advisor_student_progress(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    advisor = request.user.advisor

    if student.assigned_advisor != advisor:
        raise PermissionDenied("You are not assigned to this student")

    schedule = WorkSchedule.objects.filter(student=student, is_active=True).first()
    if not schedule:
        return render(request, 'advisors/student_daily_work_reports.html', {
            'student': student,
            'error': 'No active work schedule found.'
        })

    workdays_per_week = schedule.workdays_per_week
    tasks = Task.objects.filter(student=student).order_by('work_date')

    grouped_tasks = []
    weekly_tasks = []
    week_number = 1

    for task in tasks:
        weekly_tasks.append(task)
        if len(weekly_tasks) == workdays_per_week:
            supervisor_feedback = all(t.supervisor_feedback for t in weekly_tasks)
            advisor_feedback = all(t.advisor_feedback for t in weekly_tasks)
            supervisor_feedback_exists = any(t.supervisor_feedback for t in weekly_tasks)

            grouped_tasks.append({
                'week_number': week_number,
                'tasks': weekly_tasks,
                'is_complete': True,
                'supervisor_feedback': supervisor_feedback,
                'supervisor_feedback_exists': supervisor_feedback_exists,
                'advisor_feedback': advisor_feedback,
            })
            weekly_tasks = []
            week_number += 1

    # Handle any remaining tasks for the final (incomplete) week
    if weekly_tasks:
        supervisor_feedback = all(t.supervisor_feedback for t in weekly_tasks)
        advisor_feedback = all(t.advisor_feedback for t in weekly_tasks)
        supervisor_feedback_exists = any(t.supervisor_feedback for t in weekly_tasks)

        grouped_tasks.append({
            'week_number': week_number,
            'tasks': weekly_tasks,
            'is_complete': False,
            'supervisor_feedback': supervisor_feedback,
            'supervisor_feedback_exists': supervisor_feedback_exists,
            'advisor_feedback': advisor_feedback,
        })

    context = {
        'student': student,
        'grouped_tasks': grouped_tasks,
        'work_schedule': schedule,
    }
    return render(request, 'advisors/student_daily_work_reports.html', context)

@login_required
def advisor_provide_feedback(request, student_id, week_number):
    student = get_object_or_404(Student, user_id=student_id)
    schedule = get_object_or_404(WorkSchedule, student=student, is_active=True)
    
    # Get tasks for the week
    start_index = (week_number - 1) * schedule.workdays_per_week
    end_index = start_index + schedule.workdays_per_week
    tasks = student.tasks.all().order_by('work_date')[start_index:end_index]
    
    if request.method == 'POST':
        form = AdvisorTaskFeedbackForm(request.POST)
        if form.is_valid():
            # Save the feedback for all tasks in the week
            for task in tasks:
                task.advisor_feedback = form.cleaned_data['advisor_feedback']
                task.save()
            return redirect('student_daily_work_report', student_id=student_id)
    else:
        form = AdvisorTaskFeedbackForm()
    
    context = {
        'student': student,
        'week_number': week_number,
        'tasks': tasks,
        'form': form
    }
    return render(request, 'advisors/provide_feedback.html', context)


@login_required
def advisor_edit_feedback(request, student_id, feedback_id):
    # Retrieve the student instance based on the student_id
    student = get_object_or_404(Student, pk=student_id)

    # Ensure the logged-in user is the advisor for the student
    if student.assigned_advisor != request.user.advisor:
        raise PermissionDenied

    # Retrieve the feedback (Task) for the student and feedback_id
    feedback = get_object_or_404(Task, pk=feedback_id, student=student)

    # If the request method is POST, process the form data and update the feedback
    if request.method == 'POST':
        form = AdvisorTaskFeedbackForm(request.POST)
        if form.is_valid():
            # Update feedback for this specific task
            feedback.advisor_feedback = form.cleaned_data['advisor_feedback']
            feedback.save()  # Save the updated feedback

            # Redirect to the student's report page (or wherever you need)
            return redirect('student_daily_work_report', student_id=student.pk)
    else:
        # Use existing feedback as the initial form data
        form = AdvisorTaskFeedbackForm(initial={
            'advisor_feedback': feedback.advisor_feedback,
        })

    # Pass the feedback and student data to the context
    context = {
        'student': student,
        'feedback': feedback,
        'form': form
    }
    return render(request, 'advisors/edit_feedback.html', context)
def student_reported_tasks(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    work_schedule = WorkSchedule.objects.filter(student=student, is_active=True).first()
    
    # Calculate months completed
    total_weeks = work_schedule.workdays_per_week * 4  # Assuming 4 weeks/month
    total_months = student.task_set.count() // total_weeks
    
    # Check if all months have evaluations
    monthly_evaluations = MonthlyEvaluation.objects.filter(student=student)
    all_months_evaluated = monthly_evaluations.count() >= total_months
    
    context = {
        'student': student,
        'all_months_evaluated': all_months_evaluated,
        # ... rest of your existing context
    }
    return render(request, 'Supervisor/student_reported_tasks.html', context)

@login_required
def submit_final_evaluation(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # Safely get supervisor object
    try:
        supervisor = request.user.supervisor
    except AttributeError:
        raise PermissionDenied("Only supervisors can submit final evaluations.")

    # Check that this supervisor is assigned to this student
    if student.assigned_supervisor != supervisor:
        raise PermissionDenied("You are not assigned to this student.")

    # Get internship: from student or approved application
    internship = student.internship
    if not internship:
        approved_app = Application.objects.filter(student=student, status='Approved').first()
        internship = approved_app.internship if approved_app else None

    if not internship:
        messages.error(request, "Student does not have an internship assigned.")
        return redirect('student_reported_tasks', student_id=student_id)

    # Get active work schedule
    schedule = WorkSchedule.objects.filter(student=student, is_active=True).first()
    if not schedule:
        messages.error(request, "No active work schedule found for the student.")
        return redirect('student_reported_tasks', student_id=student_id)

    workdays_per_week = schedule.workdays_per_week
    tasks = student.tasks.all()

    # Safely calculate required vs completed tasks
    try:
        duration_months = int(internship.duration)
    except (AttributeError, ValueError):
        duration_months = 0

    required_tasks = workdays_per_week * 4 * duration_months
    completed_tasks = tasks.count()

    if completed_tasks < required_tasks:
        messages.error(
            request,
            f"Student is expected to complete {required_tasks} tasks, but only {completed_tasks} submitted."
        )
        return redirect('student_reported_tasks', student_id=student_id)

    # Prevent duplicate evaluations
    if Evaluation.objects.filter(internship=internship).exists():
        messages.warning(request, "Final evaluation already submitted.")
        return redirect('student_reported_tasks', student_id=student_id)

    # Handle form submission
    if request.method == 'POST':
        form = FinalEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.internship = internship
            evaluation.supervisor = supervisor

            # Calculate total mark
            fields = [
                'knowledge', 'problem_solving', 'quality', 'punctuality',
                'initiative', 'dedication', 'cooperation', 'discipline',
                'responsibility', 'socialization', 'communication', 'decision_making'
            ]
            total = sum(form.cleaned_data[field] for field in fields)
            evaluation.total_mark = total
            evaluation.overall_performance = (total / (len(fields) * 5)) * 100

            evaluation.save()
            messages.success(request, "Final evaluation submitted successfully!")
            return redirect('student_reported_tasks', student_id=student_id)
    else:
        form = FinalEvaluationForm()

    return render(request, 'supervisor/final_evaluation_form.html', {
        'form': form,
        'student': student,
        'required_tasks': required_tasks,
        'completed_tasks': completed_tasks,
    })


@login_required
@user_passes_test(lambda u: hasattr(u, 'student'))
def rate_company(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id)
    student = request.user.student

    rating = CompanyRating.objects.filter(student=student, internship=internship).first()

    if request.method == 'POST':
        form = CompanyRatingForm(request.POST, instance=rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.student = student
            rating.company = internship.company
            rating.internship = internship
            rating.save()
            messages.success(request, "Thank you for rating the company!")
            return redirect('student_dashboard')
    else:
        form = CompanyRatingForm(instance=rating)

    return render(request, 'students/rate_company.html', {
        'form': form,
        'internship': internship
    })


