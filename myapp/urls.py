from django.urls import path, include
from . import views
from . import consumers
from rest_framework.routers import DefaultRouter

# Initialize Router for ViewSets
router = DefaultRouter()
router.register(r'departmentheads', views.DepartmentHeadViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'advisors', views.AdvisorViewSet)
router.register(r'supervisors', views.SupervisorViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'internships', views.InternshipViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'userroles', views.UserRoleViewSet)

urlpatterns = [
    # Home page and login
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Admin URLs
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Company Admin URLs
    path('company-admin/dashboard/', views.company_admin_dashboard, name='company_admin_dashboard'),
    path('company-admin/applications/', views.manage_applications, name='manage_applications'),
    path('company-admin/toggle-applications/', views.toggle_applications, name='toggle_applications'),
    path('assign-supervisor-to-students/', views.assign_supervisor_to_students, name='assign_supervisor_to_students'),

    # User Registration URLs
    path('company/register/', views.company_register, name='register_company'),
    path('company-admin/register/', views.company_admin_register, name='company_admin_register'),
    path('advisor/add/', views.advisor_register, name='add_advisor'),
    path('register/department-head/', views.department_head_register, name='department_head_register'),
    path('register/supervisor/', views.supervisor_register, name='supervisor_register'),

    # Student URLs
     path('student/<int:user_id>/progress/', views.view_student_progress, name='view_student_progress'),
    path('evaluation/<int:evaluation_id>/pdf/', views.view_monthly_evaluation, name='view_monthly_evaluation'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/internships/', views.internship_applications, name='internship_applications'),
    path('student/progress_reports/', views.progress_reports, name='progress_reports'),
    path('student/request_support/', views.request_support, name='request_support'),
    path('student/final_report/', views.final_report, name='final_report'),
    path('student/<int:student_user_id>/assign_advisor/', views.assign_advisor, name='assign_advisor'),
    path('student/<int:user_id>/export/', views.export_student_progress, name='export_student_progress'),
    path('student/<int:user_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('student/<int:user_id>/progress/', views.view_student_progress, name='view_student_progress'),
    path('student-management/', views.student_management, name='student_management'),
    path('student/add/', views.add_student, name='add_student'),
    path('student/<int:student_id>/view/', views.view_student, name='view_student'),
    path('student/<int:student_user_id>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:student_user_id>/delete/', views.delete_student, name='delete_student'),
    path('submit-task/<int:task_id>/', views.submit_task, name='submit_task'),

    # Department Head URLs
    path('departmenthead/dashboard/', views.department_head_dashboard, name='department_head_dashboard'),
    path('department-head/update/<int:department_id>/', views.department_head_update, name='department_head_update'),
    path('department-head/create/', views.department_head_create, name='department_head_create'),
    path('departmenthead/manage_placements/', views.manage_placements, name='manage_placements'),
    path('departmenthead/student_progress/', views.student_progress, name='student_progress'),
    path('departmenthead/generate_reports/', views.generate_reports, name='generate_reports'),
    path('departmenthead/advisor_management/', views.advisor_management, name='advisor_management'),
    path('departmenthead/set_policies/', views.set_policies, name='set_policies'),

    # Industry Supervisor URLs
    path('supervisor/dashboard/', views.industry_supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/student-activity/<int:student_id>/', views.student_activity, name='student_activity'),
    path('supervisor/assigned-students/', views.assigned_students, name='assigned_students'),
    path('supervisor/<int:supervisor_id>/delete/', views.delete_supervisor, name='delete_supervisor'),
    path('supervisor/<int:supervisor_id>/update/', views.update_supervisor, name='update_supervisor'),
    path('supervisor/<int:supervisor_id>/', views.view_supervisor_details, name='view_supervisor_details'),
    path('supervisors/', views.supervisor_list, name='supervisor_list'),
    path('supervisor/manage_tasks/', views.manage_tasks, name='manage_tasks'),
    path('supervisor/monitor_performance/', views.monitor_performance, name='monitor_performance'),
    path('supervisor/provide_feedback/', views.provide_feedback, name='provide_feedback'),
    path('supervisor/communication/', views.communication, name='supervisor_communication'),

    # University Advisor URLs
    path('advisor/dashboard/', views.advisor_dashboard, name='advisor_dashboard'),
    path('advisor/<int:advisor_id>/assigned_students/', views.advisor_assigned_students, name='advisor_assigned_students'),
    path('advisor/<int:advisor_user_id>/view/', views.view_advisor_details, name='view_advisor_details'),
    path('advisor/<int:advisor_user_id>/send-message/', views.send_message, name='send_message'),
    path('advisor/<int:advisor_user_id>/update/', views.update_advisor, name='update_advisor'),
    path('advisor-management/', views.advisor_management, name='advisor_management'),
    path('advisor/<int:advisor_id>/delete/', views.delete_advisor, name='delete_advisor'),
    path('advisor/review_applications/', views.review_applications, name='review_applications'),
    path('advisor/reports/', views.reports, name='advisor_reports'),
    path('advisor/give_feedback/', views.give_feedback, name='advisor_give_feedback'),
    path('advisor/performance_evaluation/', views.performance_evaluation, name='advisor_performance_evaluation'),
    path('advisor/communication/', views.communication, name='advisor_communication'),

    # Department URLs
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/update/<int:pk>/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/delete/<int:pk>/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Company URLs
    path('company-management/', views.company_management, name='company_management'),
    path('company/add/', views.add_company, name='add_company'),
    path('company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('company/<int:company_id>/delete/', views.delete_company, name='delete_company'),
    path('view_company/<int:company_id>/', views.view_company, name='view_company'),
    path('company/feedback/', views.submit_company_feedback, name='submit_company_feedback'),
    path('company/export/', views.export_company_data, name='export_company_data'),

    # CompanyAdmin URLs
    path('company-admin/post-internship/', views.post_internship, name='post_internship'),
    path('company-admin/view-internships/', views.view_internships, name='view_internships'),
    path('company-admins/', views.CompanyAdminListView.as_view(), name='company_admin_list'),
    path('company-admins/create/', views.company_admin_register, name='company_admin_create'),
    path('company-admins/update/<int:pk>/', views.CompanyAdminUpdateView.as_view(), name='company_admin_update'),
    path('company-admins/delete/<int:pk>/', views.CompanyAdminDeleteView.as_view(), name='company_admin_delete'),

    # Role URLs
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/create/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/update/<int:pk>/', views.RoleUpdateView.as_view(), name='role_update'),
    path('roles/delete/<int:pk>/', views.RoleDeleteView.as_view(), name='role_delete'),

    # UserRole URLs
    path('user-roles/', views.UserRoleListView.as_view(), name='user_role_list'),
    path('user-roles/create/', views.UserRoleCreateView.as_view(), name='user_role_create'),
    path('user-roles/update/<int:pk>/', views.UserRoleUpdateView.as_view(), name='user_role_update'),
    path('user-roles/delete/<int:pk>/', views.UserRoleDeleteView.as_view(), name='user_role_delete'),

    # CustomField URLs
    path('custom-fields/', views.CustomFieldListView.as_view(), name='custom_field_list'),
    path('custom-fields/create/', views.CustomFieldCreateView.as_view(), name='custom_field_create'),
    path('custom-fields/update/<int:pk>/', views.CustomFieldUpdateView.as_view(), name='custom_field_update'),
    path('custom-fields/delete/<int:pk>/', views.CustomFieldDeleteView.as_view(), name='custom_field_delete'),

    # CustomFieldValue URLs
    path('custom-field-values/', views.CustomFieldValueListView.as_view(), name='custom_field_value_list'),
    path('custom-field-values/create/', views.CustomFieldValueCreateView.as_view(), name='custom_field_value_create'),
    path('custom-field-values/update/<int:pk>/', views.CustomFieldValueUpdateView.as_view(), name='custom_field_value_update'),
    path('custom-field-values/delete/<int:pk>/', views.CustomFieldValueDeleteView.as_view(), name='custom_field_value_delete'),

    # Other URLs
    path('role-selection/', views.RoleSelectionView.as_view(), name='role_selection'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/update/<int:pk>/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
    path('internship-activity/', views.internship_activity, name='internship_activity'),
    path('generate-evaluation-form/', views.generate_evaluation_form, name='generate_evaluation_form'),
    path('form-generated/', views.form_generated, name='form_generated'),
    path('generate-logbook-form/', views.generate_logbook_form, name='generate_logbook_form'),
    path('form-list/', views.form_list, name='form_list'),
    path('communication/', views.communication_page, name='communication_page'),
    path('private_chat/<int:user_id>/', views.private_chat, name='private_chat'),


    # urls.py
    path('manage_group/<int:group_id>/', views.manage_group, name='manage_group'),
    path('messages/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
   
    path('chat/<str:role>/', views.private_chat_list, name='private_chat_list'),
    
    

    path('group/<int:group_id>/', views.group_chat, name='group_chat'),
    path('group/list/', views.list_chat_groups, name='list_chat_groups'),
    path('chat/company_admin/<int:company_id>/', views.chat_with_company_admin, name='chat_with_company_admin'),
    path('company/<int:company_id>/supervisors/', views.company_supervisors, name='company_supervisors'),

    # Internship URLs
    path('internships/update/<int:internship_id>/', views.update_internship, name='update_internship'),
    path('internships/delete/<int:internship_id>/', views.delete_internship, name='delete_internship'),
    path('internships/toggle-status/<int:internship_id>/', views.toggle_internship_status, name='toggle_internship_status'),
    path('internships/<int:internship_id>/applicants/', views.applicant_list, name='applicant_list'),
    path('internships/<int:internship_id>/apply/', views.apply_internship, name='apply_internship'),
    path('existing-internships/', views.existing_internships, name='existing_internships'),

    # Application URLs
    path('applications/<int:application_id>/accept/', views.accept_application, name='accept_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),

    # Feedback and Task URLs
    path('feedback/', views.supervisor_feedback_view, name='supervisor_feedback'),
    path('student/<int:student_id>/tasks/', views.student_progress_view, name='student_reported_tasks'),
    path('assign-workdays/', views.assign_workdays, name='assign_workdays'),
    path('provide-feedback/<int:student_id>/week/<int:week_number>/',views.provide_weekly_feedback,
    name='provide_weekly_feedback'),
    path('submit-daily-task/', views.submit_daily_task, name='submit_daily_task'),
    path('view-submitted-tasks/', views.view_submitted_tasks, name='view_submitted_tasks'),

    # Grant Chat Group Permissions
    path('grant-permissions/', views.list_internships_for_permission, name='list_internships_for_permission'),
    path('grant-permissions/<int:internship_id>/',views.list_students_for_permission, name='list_students_for_permission'),
   

    # Student Chat Group URLs
    path('groups/<int:group_id>/', views.group_chat, name='group_chat'),

    # API URLs
    # Group Creation URLs
    path('groups/department/create/', views.create_department_group, name='create_department_group'),
    path('groups/advisor/create/', views.create_advisor_group, name='create_advisor_group'),
    path('groups/supervisor/create/',views.create_supervisor_group, name='create_supervisor_group'),
    path('groups/student/create/', views.create_student_group, name='create_student_group'),

    # Group Chat URLs
   
    path('group/<int:group_id>/send/', views.send_group_message, name='send_group_message'),

    path('clear-chat/<int:user_id>/', views.clear_chat_history, name='clear_chat_history'),
    
    path('api/', include(router.urls)),




path('ws/group_chat/<int:group_id>/', consumers.GroupChatConsumer.as_asgi()),
path('messages/<int:message_id>/edit/', views.edit_message, name='edit_message'),
path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
path('groups/<int:group_id>/manage/', views.manage_group, name='manage_group'),

path('supervisor/<int:student_id>/evaluation/month/<int:month_number>/edit/',views.edit_monthly_evaluation,name='edit_monthly_evaluation'
),

# urls.py
path('internship/<int:pk>/', views.internship_detail, name='internship_detail'),
path('advisor/student/<int:student_id>/feedback/<int:week_number>/',views.advisor_provide_feedback,name='advisor_provide_feedback'),
  path('advisor/student/<int:student_id>/feedback/<int:feedback_id>/edit/', views.advisor_edit_feedback, name='advisor_edit_feedback'),
path('student/<int:student_id>/daily-reports/', views.advisor_student_progress, name='student_daily_work_report'),
path('student/<int:student_id>/monthly-evaluation/<int:month_number>/', views.submit_monthly_evaluation, name='submit_monthly_evaluation'),
path('supervisor/<int:student_id>/feedback/week/<int:week_number>/edit/', views.edit_weekly_feedback, name='edit_weekly_feedback'),
path('student/<int:student_id>/evaluation/<int:month_number>/',views.view_monthly_evaluation, name='view_monthly_evaluation'),
]