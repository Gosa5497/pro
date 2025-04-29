from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Department Name")
    description = models.TextField(verbose_name="Department Description")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


# Custom User Model
class User(AbstractUser):
    # Role Flags
    is_department_head = models.BooleanField(default=False, verbose_name="Is Department Head")
    is_advisor = models.BooleanField(default=False, verbose_name="Is Advisor")
    is_student = models.BooleanField(default=False, verbose_name="Is Student")
    is_supervisor = models.BooleanField(default=False, verbose_name="Is Supervisor")
    is_company_admin = models.BooleanField(default=False, verbose_name="Is Company Admin")

    # Common Fields
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name="Profile Image")

    # Fix auth model conflicts
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        verbose_name="Groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        verbose_name="User Permissions"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

# Company Model
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Company Name")
    industry = models.CharField(max_length=100, verbose_name="Industry")
    location = models.CharField(max_length=255, verbose_name="Location")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    contact_email = models.EmailField(verbose_name="Contact Email")
    contact_phone = models.CharField(max_length=20, verbose_name="Contact Phone")
    description = models.TextField(verbose_name="Description")

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        """
        Calculate average rating from student reviews
        Returns 0 if no ratings exist
        """
        return self.companyrating_set.aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating'] or 0.0

    @property
    def rating_count(self):
        """Return total number of ratings received"""
        return self.companyrating_set.count()

    def get_rating_display(self):
        """Formatted rating string with 1 decimal place"""
        return f"{self.average_rating:.1f}/5.0"

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['name']
# Company Feedback Model
class CompanyFeedback(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='feedbacks', verbose_name="Company")
    feedback = models.TextField(verbose_name="Feedback")
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_company_feedbacks', verbose_name="Submitted By")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"Feedback for {self.company.name} by {self.submitted_by.get_full_name()}"

    class Meta:
        verbose_name = "Company Feedback"
        verbose_name_plural = "Company Feedbacks"

# Department Head Model
class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
    position = models.CharField(max_length=100, default="Department Head", verbose_name="Position")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"

    class Meta:
        verbose_name = "Department Head"
        verbose_name_plural = "Department Heads"
# Company Admin Model
class CompanyAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Company")
    can_assign_supervisor = models.BooleanField(default=True, verbose_name="Can Assign Supervisor")
    can_manage_applications = models.BooleanField(default=True, verbose_name="Can Manage Applications")
    can_manage_internships = models.BooleanField(default=True, verbose_name="Can Manage Internships")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"

    class Meta:
        verbose_name = "Company Admin"
        verbose_name_plural = "Company Admins"


# Advisor Model
class Advisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
    office_location = models.CharField(max_length=255, verbose_name="Office Location")

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = "Advisor"
        verbose_name_plural = "Advisors"


# Supervisor Model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Company")
    position = models.CharField(max_length=100, verbose_name="Position")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"

    class Meta:
        verbose_name = "Supervisor"
        verbose_name_plural = "Supervisors"


class Internship(models.Model):
    # Duration Choices
    DURATION_CHOICES = [
        ('1', '1 Month'),
        ('2', '2 Months'),
        ('3', '3 Months'),
        ('6', '6 Months'),
        ('12', '1 Year'),
    ]

    # Training Format
    TRAINING_FORMAT_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('project_based', 'Project-based'),
    ]

    # Core Fields
    is_open = models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=3, choices=DURATION_CHOICES, default='3')
    training_format = models.CharField(max_length=20, choices=TRAINING_FORMAT_CHOICES, default='full_time')

    # Flexible Training Types
    training_types = models.JSONField(
        default=list,
        help_text="List the specific training types (e.g., ['CCNA Certification', 'Python Programming', 'Cloud Security'])"
    )

    # Qualifications (optional or required)
    required_qualifications = models.JSONField(
        default=list,
        help_text="List of qualifications required for the internship."
    )
    optional_qualifications = models.JSONField(
        default=list,
        help_text="List of optional qualifications for the internship."
    )

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    def save(self, *args, **kwargs):
        # Ensure training_types is always a list
        if isinstance(self.training_types, str):
            self.training_types = [t.strip() for t in self.training_types.split(',')]
        if isinstance(self.required_qualifications, str):
            self.required_qualifications = [q.strip() for q in self.required_qualifications.split(',')]
        if isinstance(self.optional_qualifications, str):
            self.optional_qualifications = [q.strip() for q in self.optional_qualifications.split(',')]
        super().save(*args, **kwargs)

    @property
    def formatted_training_types(self):
        """Returns training types as a comma-separated string"""
        return ', '.join(self.training_types) if self.training_types else "Not specified"

    @property
    def formatted_required_qualifications(self):
        """Returns required qualifications as a comma-separated string"""
        return ', '.join(self.required_qualifications) if self.required_qualifications else "Not specified"

    @property
    def formatted_optional_qualifications(self):
        """Returns optional qualifications as a comma-separated string"""
        return ', '.join(self.optional_qualifications) if self.optional_qualifications else "Not specified"
# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
    major = models.CharField(max_length=100, verbose_name="Major")
    year = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Year of Study"
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        verbose_name="Resume"
    )
    status = models.CharField(max_length=50, default='Active', verbose_name="Status")
    assigned_advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assigned Advisor")
    assigned_supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assigned Supervisor")
    internship = models.ForeignKey(Internship, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Internship")

    def __str__(self):
        return self.user.get_full_name()

    def task_reports_count(self):
        return self.task_set.count()
    def get_ratable_internships(self):
        return Internship.objects.filter(
            student=self,
            final_evaluation_submitted=True
        ).exclude(
            company_rating__student=self
        )

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


# Application Model
class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending', verbose_name="Status")
    cover_letter = models.TextField(null=True, blank=True, verbose_name="Cover Letter")
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, verbose_name="Internship")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Student")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"Application {self.id} - Status: {self.status}"

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Is Read")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    link = models.URLField(blank=True, null=True, verbose_name="Link")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username}"


# Feedback Model
class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedbacks', verbose_name="Student")
    feedback = models.TextField(verbose_name="Feedback")
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_feedbacks', verbose_name="Submitted By")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"Feedback for {self.student.user.get_full_name()} by {self.submitted_by.get_full_name()}"

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"


# Role Model (RBAC)
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Role Name")
    description = models.TextField(verbose_name="Description")
    permissions = models.ManyToManyField(Permission, blank=True, verbose_name="Permissions")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


# User Role Mapping
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name="Role")

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


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
    name = models.CharField(max_length=50, verbose_name="Field Name")
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES, verbose_name="Entity Type")
    field_type = models.CharField(max_length=10, choices=FIELD_TYPES, verbose_name="Field Type")
    is_required = models.BooleanField(default=False, verbose_name="Is Required")

    def __str__(self):
        return f"{self.entity_type} Field: {self.name}"

    class Meta:
        verbose_name = "Custom Field"
        verbose_name_plural = "Custom Fields"


# Custom Field Value Model
class CustomFieldValue(models.Model):
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, verbose_name="Field")
    entity_id = models.PositiveIntegerField(verbose_name="Entity ID")
    value = models.TextField(verbose_name="Value")

    class Meta:
        unique_together = ('field', 'entity_id')
        verbose_name = "Custom Field Value"
        verbose_name_plural = "Custom Field Values"

    def __str__(self):
        return f"{self.field.name}: {self.value}"


# Form Template Model
class FormTemplate(models.Model):
    FORM_TYPES = [
        ('attendance', 'Attendance Form'),
        ('activity_evaluation', 'Activity Evaluation Form'),
        ('performance_evaluation', 'Performance Evaluation Form'),
        ('monthly_progress', 'Monthly Progress Report Form'),
        ('final_evaluation', 'Final Internship Evaluation Form'),
    ]
    form_type = models.CharField(max_length=50, choices=FORM_TYPES, verbose_name="Form Type")
    description = models.TextField(verbose_name="Description")
    fields = models.JSONField(verbose_name="Fields")

    def __str__(self):
        return self.get_form_type_display()

    class Meta:
        verbose_name = "Form Template"
        verbose_name_plural = "Form Templates"

#*****************Chat Groups and Messaging********************

from django.contrib.auth import get_user_model


User = get_user_model()

class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    participants = models.ManyToManyField(User, related_name='chat_groups')
    admins = models.ManyToManyField(User, related_name='managed_groups')
    group_image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, null=True, blank=True, on_delete=models.SET_NULL)
    supervisor = models.ForeignKey(Supervisor, null=True, blank=True, on_delete=models.SET_NULL)
    internship = models.ForeignKey(Internship, null=True, blank=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Group type (private/public/channel)
    GROUP_TYPES = (
        ('private', 'Private Group'),
        ('public', 'Public Group'),
        ('channel', 'Channel'),
    )
    group_type = models.CharField(max_length=10, choices=GROUP_TYPES, default='private')

    def __str__(self):
        return self.name

    def can_edit(self, user):
        return user == self.created_by or user in self.admins.all()

    def soft_delete(self):
        self.is_active = False
        self.save()
    def can_communicate(self, user):
        """Improved permission check with proper indentation and logic"""
        if not user.is_authenticated:
            return False
            
        # Check if user is a direct participant
        if user in self.participants.all():
            return True

        # Department-based groups
        if self.department:
            if hasattr(user, 'student') and user.student.department == self.department:
                return True
            if hasattr(user, 'departmenthead') and user.departmenthead.department == self.department:
                return True
            return False

        # Advisor-based groups
        if self.advisor:
            if hasattr(user, 'student') and user.student.assigned_advisor == self.advisor:
                return True
            if hasattr(user, 'advisor') and user.advisor == self.advisor:
                return True
            return False

        # Supervisor-based groups
        if self.supervisor:
            if hasattr(user, 'student') and user.student.assigned_supervisor == self.supervisor:
                return True
            if hasattr(user, 'supervisor') and user.supervisor == self.supervisor:
                return True
            return False

        # Internship-based groups
        if self.internship:
            if hasattr(user, 'student'):
                return Application.objects.filter(
                    student=user.student,
                    internship=self.internship,
                    status='Approved'
                ).exists()
            return False

        return False
    def add_participants(self):
        """
        Automatically add participants based on the group's relationships.
        Includes the Department Head for department groups.
        """
        if self.department:
            # Add students from the department
            students = Student.objects.filter(department=self.department)
            self.participants.add(*[s.user for s in students])
            
            # Add the Department Head of this department
            department_head = DepartmentHead.objects.filter(department=self.department).first()
            if department_head:
                self.participants.add(department_head.user)
            
        elif self.advisor:
            # Add students assigned to the advisor
            students = Student.objects.filter(assigned_advisor=self.advisor)
            self.participants.add(*[s.user for s in students])
            
        elif self.supervisor:
            # Add students assigned to the supervisor
            students = Student.objects.filter(assigned_supervisor=self.supervisor)
            self.participants.add(*[s.user for s in students])
            
        elif self.internship:
            # Add students with approved internships
            students = Student.objects.filter(
                application__internship=self.internship,
                application__status='Approved'
            ).distinct()
            self.participants.add(*[s.user for s in students])

class GroupMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('deleted', 'Deleted'),
    )

    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)

    # For message replies/threads
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender} - {self.get_message_type_display()}"

    def can_edit(self, user):
        return user == self.sender or user in self.group.admins.all()

    def can_delete(self, user):
        return user == self.sender or user in self.group.admins.all()

    def soft_delete(self):
        self.deleted = True
        self.content = ""
        self.file = None
        self.message_type = 'deleted'
        self.save()

    def mark_as_edited(self):
        self.edited = timezone.now()
        self.save()

class PrivateMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('deleted', 'Deleted'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='private_chat_files/', null=True, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    read = models.BooleanField(default=False)

    # For message replies
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sender} to {self.receiver} - {self.get_message_type_display()}"

    def can_edit(self, user):
        return user == self.sender

    def can_delete(self, user):
        return user == self.sender

    def soft_delete(self):
        self.deleted = True
        self.content = ""
        self.file = None
        self.message_type = 'deleted'
        self.save()

    def mark_as_edited(self):
        self.edited = timezone.now()
        self.save()
# Chat Message Model
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sent_messages', verbose_name="Sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_received_messages', verbose_name="Receiver")
    content = models.TextField(verbose_name="Content")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    read = models.BooleanField(default=False, verbose_name="Is Read")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"From {self.sender} to {self.receiver} - {self.timestamp}"
      
#***************Evaluations and feedback********************

class Task(models.Model):
    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[('completed', 'Completed'), ('pending', 'Pending')]
    )
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='tasks')
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE, related_name='tasks')
    work_date = models.DateField(help_text="Date the task was performed.")
    description = models.TextField(help_text="Task details.")
    completed = models.BooleanField(default=False) 
    supervisor_feedback = models.TextField(blank=True, null=True, help_text="Feedback from supervisor.")
    advisor_feedback = models.TextField(blank=True, null=True, help_text="Feedback from advisor.")
    created_at = models.DateTimeField(auto_now_add=True)

    def can_edit_or_delete(self):
        return now() <= self.created_at + timedelta(hours=24)

    def __str__(self):
        return f"Task for {self.student.user.get_full_name()} on {self.work_date}"

    def clean(self):
        if self.advisor_feedback and not self.supervisor_feedback:
            raise ValidationError("Advisor feedback can only be given after the supervisor has provided feedback.")

    @property
    def computed_week_number(self):
        try:
            schedule = WorkSchedule.objects.get(student=self.student, is_active=True)
            days_since_start = (self.work_date - schedule.created_at.date()).days
            return (days_since_start // 7) + 1
        except WorkSchedule.DoesNotExist:
            return None

class WorkSchedule(models.Model):
    student = models.ForeignKey(
        'Student', 
        on_delete=models.CASCADE,
        related_name='work_schedules'
    )
    supervisor = models.ForeignKey(
        'Supervisor',
        on_delete=models.CASCADE,
        related_name='managed_schedules'
    )
    workdays_per_week = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text="Number of required task submissions per week"
    )
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'is_active')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.workdays_per_week} tasks/week"

    def clean(self):
        if self.workdays_per_week < 1:
            raise ValidationError("At least 1 workday per week is required")

    def current_week(self):
        """Calculate current week based on creation date"""
        today = timezone.now().date()
        days_since_start = (today - self.created_at.date()).days
        return (days_since_start // 7) + 1
    def get_week_range(self, week_number):
        """
        Get first and last task for a given week number
        Returns tuple (first_task_date, last_task_date)
        """
        tasks = self.student.task_set.order_by('work_date')
        start_idx = (week_number - 1) * self.workdays_per_week
        end_idx = start_idx + self.workdays_per_week
        
        week_tasks = tasks[start_idx:end_idx]
        if not week_tasks:
            return (None, None)
            
        return (week_tasks.first().work_date, week_tasks.last().work_date)

    def is_week_complete(self, week_number):
        """Check if the required reports for this week are submitted"""
        reports = DailyWorkReport.objects.filter(
            student=self.student,
            week_number=week_number,
            status='submitted'
        )
        return reports.count() >= self.workdays_per_week

class DailyWorkReport(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_reports')
    work_date = models.DateField()
    week_number = models.PositiveIntegerField(editable=False)
    tasks = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    supervisor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'work_date')
        ordering = ['-work_date']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.work_date}"

    def save(self, *args, **kwargs):
        # Auto-calculate week number
        schedule = WorkSchedule.objects.get(student=self.student, is_active=True)
        days_since_start = (self.work_date - schedule.start_date).days
        self.week_number = (days_since_start // 7) + 1
        super().save(*args, **kwargs)

    def is_workday(self):
        """Check if report date is a valid workday"""
        schedule = WorkSchedule.objects.get(student=self.student, is_active=True)
        return self.work_date.weekday() in schedule.assigned_days

class WeeklyFeedback(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    supervisor = models.ForeignKey('Supervisor', on_delete=models.CASCADE)
    week_number = models.PositiveIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    week_start_date = models.DateField(blank=True, null=True)  # Ensure this field is defined

    class Meta:
        unique_together = ('student', 'week_number')
        ordering = ['-week_number']

    def __str__(self):
        return f"Week {self.week_number} Feedback for {self.student.user.get_full_name()}"

    def is_complete(self):
        """Check if all daily reports for week are submitted"""
        reports = DailyWorkReport.objects.filter(
            student=self.student,
            week_number=self.week_number,
            status='submitted'
        )
        schedule = WorkSchedule.objects.get(student=self.student, is_active=True)
        return reports.count() >= schedule.workdays_per_week
# models.py
class MonthlyEvaluation(models.Model):
    CATEGORY_LIMITS = {
        'general': 25,
        'personal': 25,
        'professional': 50
    }

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='evaluations')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    month_number = models.PositiveIntegerField(blank=True, null=True)
    month = models.CharField(max_length=20)
    total_score = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # General Performance (25%)
    punctuality = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    reliability = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    independence = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    communication = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    professionalism = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)

    # Personal Performance (25%)
    speed_of_work = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    accuracy = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    engagement = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    need_for_work = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    cooperation = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)

    # Professional Skills (50%)
    technical_skills = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    organizational_skills = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    project_support = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    responsibility = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    team_quality = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)], default=0)  # Removed MaxValueValidator(5)

    def calculate_total_score(self):
        return sum([
            self.punctuality, self.reliability, self.independence,
            self.communication, self.professionalism, self.speed_of_work,
            self.accuracy, self.engagement, self.need_for_work, self.cooperation,
            self.technical_skills, self.organizational_skills, self.project_support,
            self.responsibility, self.team_quality
        ])

    def get_category_progress(self):
        return {
            'general': {
                'current': sum([self.punctuality, self.reliability, self.independence,
                                self.communication, self.professionalism]),
                'max': self.CATEGORY_LIMITS['general']
            },
            'personal': {
                'current': sum([self.speed_of_work, self.accuracy, self.engagement,
                                self.need_for_work, self.cooperation]),
                'max': self.CATEGORY_LIMITS['personal']
            },
            'professional': {
                'current': sum([self.technical_skills, self.organizational_skills,
                                self.project_support, self.responsibility, self.team_quality]),
                'max': self.CATEGORY_LIMITS['professional']
            }
        }

    class Meta:
        unique_together = ('student', 'month_number')
        ordering = ['-month_number']

class Evaluation(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    
    # Section A: Job Performance (1-5 scale)
    knowledge = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    problem_solving = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    quality = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    punctuality = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    initiative = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    
    # Section B: Soft Skills (1-5 scale)
    dedication = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    cooperation = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    discipline = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    responsibility = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    socialization = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    communication = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    decision_making = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)
    
    # Section C: Comments & Job Offer
    potential_comments = models.TextField()
    job_offer = models.BooleanField(default=False)
    
    # Calculated fields
    total_mark = models.PositiveSmallIntegerField(editable=False)  # Auto-calculated (sum of all scores)
    overall_performance = models.FloatField(editable=False)  # (total_mark/60)*20
# models.py
class CompanyRating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1 (Poor) - 5 (Excellent)"
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'internship')

    def __str__(self):
        return f"{self.student} rated {self.company} - {self.rating}/5"
#**************chatboot******************
