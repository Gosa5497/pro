from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# Custom User Model
class User(AbstractUser):
    # Role Flags
    is_department_head = models.BooleanField(default=False)
    is_advisor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_company_admin = models.BooleanField(default=False)
    # Common Fields
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    # Fix auth model conflicts
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True
    )

    def __str__(self):
        return self.username

# Department Head Model
class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, default="Department Head")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"

# Company Model
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.name
    
# companyadmin models.py
class CompanyAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    can_assign_supervisor = models.BooleanField(default=True)
    can_manage_applications = models.BooleanField(default=True)
    can_manage_internships = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"
# Advisor Model
class Advisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    office_location = models.CharField(max_length=255)

    def __str__(self):
        return self.user.get_full_name()
class CompanyFeedback(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='feedbacks')
    feedback = models.TextField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_company_feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.company.name} by {self.submitted_by.get_full_name()}"
# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    major = models.CharField(max_length=100)
    year = models.IntegerField()
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    status = models.CharField(max_length=50, default='Active')
    assigned_advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

# Supervisor Model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"

# Internship Model
class Internship(models.Model):
    is_open = models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    title=models.CharField(max_length=50,blank=False)
    description = models.TextField(blank=True)
    

    def __str__(self):
        return self.title 
# Application Model
class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    cover_letter = models.TextField(null=True, blank=True)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application {self.id} - Status: {self.status}"
# Task Model
class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    description = models.TextField()
    deadline = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        ordering = ['deadline']

# Evaluation Model
class Evaluation(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    criteria = models.TextField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    comments = models.TextField(blank=True, null=True)

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        
class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedbacks')
    feedback = models.TextField()
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.student.user.get_full_name()} by {self.submitted_by.get_full_name()}"
# Role Model (RBAC)
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name

# User Role Mapping
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')

# Custom Field System
class CustomField(models.Model):
    ENTITY_TYPES = [
        ('Student', 'Student'),
        ('Company', 'Company'),
        ('Task', 'Task'),
        ('Internship', 'Internship'),
    ]
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
    ]
    
    name = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.entity_type} Field: {self.name}"

class CustomFieldValue(models.Model):
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE)
    entity_id = models.PositiveIntegerField()
    value = models.TextField()

    class Meta:
        unique_together = ('field', 'entity_id')

    def __str__(self):
        return f"{self.field.name}: {self.value}"

class FormTemplate(models.Model):
    FORM_TYPES = [
        ('attendance', 'Attendance Form'),
        ('activity_evaluation', 'Activity Evaluation Form'),
        ('performance_evaluation', 'Performance Evaluation Form'),
        ('monthly_progress', 'Monthly Progress Report Form'),
        ('final_evaluation', 'Final Internship Evaluation Form'),
    ]
    form_type = models.CharField(max_length=50, choices=FORM_TYPES)
    description = models.TextField()
    fields = models.JSONField()  # Store form fields as JSON

    def __str__(self):
        return self.get_form_type_display()
class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='chat_groups')
    is_private = models.BooleanField(default=False)  # For private chats
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.receiver} - {self.timestamp}"


class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='private_sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='private_received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
