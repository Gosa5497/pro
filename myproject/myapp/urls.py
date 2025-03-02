from django.urls import path, include
from . import views
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
router.register(r'evaluations', views.EvaluationViewSet)
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
    path('company-admin/assign-supervisor/<int:application_id>/', views.assign_supervisor, name='assign_supervisor'),
    path('company-admin/toggle-applications/', views.toggle_applications, name='toggle_applications'),

    # User Registration URLs
    path('company/register/', views.company_register, name='register_company'),
    path('company-admin/register/', views.company_admin_register, name='company_admin_register'),
    path('register/department/', views.register_department, name='register_department'),
    path('register/student/', views.student_register, name='student_register'),
    path('advisor/add/', views.advisor_register, name='add_advisor'),
    path('register/department-head/', views.department_head_register, name='department_head_register'),
    path('register/supervisor/', views.supervisor_register, name='supervisor_register'),

    # Student URLs
    path('student/<int:user_id>/export/', views.export_student_progress, name='export_student_progress'),
    path('student/<int:user_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('student/<int:user_id>/progress/', views.view_student_progress, name='view_student_progress'),
    path('student-management/', views.student_management, name='student_management'),
    path('student/add/', views.add_student, name='add_student'),
    path('student/<int:student_id>/view/', views.view_student, name='view_student'),
    path('student/<int:student_user_id>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:student_user_id>/delete/', views.delete_student, name='delete_student'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/internships/', views.internship_applications, name='internship_applications'),
    path('student/progress_reports/', views.progress_reports, name='progress_reports'),
    path('student/feedback/', views.feedback, name='feedback'),
    path('student/request_support/', views.request_support, name='request_support'),
    path('student/final_report/', views.final_report, name='final_report'),

    # Department Head URLs
    path('department-head/update/<int:department_id>/', views.department_head_update, name='department_head_update'),
    path('department-head/create/', views.department_head_create, name='department_head_create'),
    path('departmenthead/dashboard/', views.department_head_dashboard, name='department_head_dashboard'),
    path('departmenthead/manage_placements/', views.manage_placements, name='manage_placements'),
    path('departmenthead/student_progress/', views.student_progress, name='student_progress'),
    path('departmenthead/generate_reports/', views.generate_reports, name='generate_reports'),
    path('departmenthead/advisor_management/', views.advisor_management, name='advisor_management'),
    path('departmenthead/set_policies/', views.set_policies, name='set_policies'),

    # Industry Supervisor URLs
    path('supervisor/dashboard/', views.industry_supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/assigned_students/', views.assigned_students, name='assigned_students'),
    path('supervisor/manage_tasks/', views.manage_tasks, name='manage_tasks'),
    path('supervisor/monitor_performance/', views.monitor_performance, name='monitor_performance'),
    path('supervisor/provide_feedback/', views.provide_feedback, name='provide_feedback'),
    path('supervisor/communication/', views.communication, name='supervisor_communication'),

    # University Advisor URLs
    path('advisor/<int:advisor_user_id>/view/', views.view_advisor_details, name='view_advisor_details'),
    path('advisor/<int:advisor_user_id>/send-message/', views.send_message, name='send_message'),
    path('advisor/<int:advisor_user_id>/update/', views.update_advisor, name='update_advisor'),
    path('advisor-management/', views.advisor_management, name='advisor_management'),
    path('advisor/<int:advisor_id>/delete/', views.delete_advisor, name='delete_advisor'),
    path('advisor/dashboard/', views.advisor_dashboard, name='advisor_dashboard'),
    path('advisor/review_applications/', views.review_applications, name='review_applications'),
    path('advisor/assigned_students/', views.assigned_students, name='advisor_assigned_students'),
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

     
    path('chat/advisors/', views.private_chat_list, {'role': 'advisors'}, name='chat_advisors'),
    path('chat/company-admins/', views.private_chat_list, {'role': 'company_admins'}, name='chat_company_admins'),
    path('chat/supervisors/', views.private_chat_list, {'role': 'supervisors'}, name='chat_supervisors'),
    path('chat/group/create/', views.create_chat_group, name='create_chat_group'),
    path('group/students/', views.group_chat_students, name='group_chat_students'),  # Add this line
    path('chat/private/<int:user_id>/', views.private_chat, name='private_chat'),
    

     # Group Chat URLs
    path('group/<int:group_id>/', views.group_chat, name='group_chat'),
    path('group/create/', views.create_chat_group, name='create_chat_group'),
    path('group/list/', views.list_chat_groups, name='list_chat_groups'),

    path('internships/update/<int:internship_id>/', views.update_internship, name='update_internship'),
    path('internships/delete/<int:internship_id>/', views.delete_internship, name='delete_internship'),
    path('internships/toggle-status/<int:internship_id>/', views.toggle_internship_status, name='toggle_internship_status'),

    path('applications/<int:application_id>/accept/', views.accept_application, name='accept_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'), 
    path('internships/<int:internship_id>/applicants/', views.applicant_list, name='applicant_list'),
    path('internships/<int:internship_id>/apply/', views.apply_internship, name='apply_internship'),
    path('internships/apply/<int:internship_id>/', views.apply_internship, name='apply_internship'),
    path('existing-internships/', views.existing_internships, name='existing_internships'),
    path('api/', include(router.urls)),
]