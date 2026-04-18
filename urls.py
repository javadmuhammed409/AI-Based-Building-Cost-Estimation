from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_project/', views.create_project, name='create_project'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/approve/', views.approve_project, name='approve_project'),
    path('project/<int:pk>/assign/', views.assign_contractor, name='assign_contractor'),
    path('ai-estimator/', views.ai_estimation, name='ai_estimation'),
    path('task/<int:pk>/update/', views.update_task_status, name='update_task_status'),
    path('dashboard/rates/', views.update_material_rates, name='update_material_rates'),
    path('smart-budget/', views.budget_estimation, name='budget_estimation'),
    path('dashboard/users/', views.user_list, name='user_list'),
    path('dashboard/users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    
    # Shopping & Material Requests
    path('shop/', views.shop, name='shop'),
    path('shop/manage/', views.manage_products, name='manage_products'),
    path('shop/add/', views.add_product, name='add_product'),
    path('shop/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('shop/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('shop/request/<int:pk>/', views.request_product, name='request_product'),
    path('dashboard/requests/', views.contractor_requests, name='contractor_requests'),
    path('dashboard/requests/<int:pk>/<str:status>/', views.update_request_status, name='update_request_status'),
    path('dashboard/designs/add/', views.add_design, name='add_design'),
    
    # House Design Gallery (Admin & User)
    path('dashboard/house-designs/', views.admin_manage_designs, name='admin_manage_designs'),
    path('dashboard/house-designs/delete/<int:pk>/', views.admin_delete_design, name='admin_delete_design'),
    path('gallery/', views.house_design_gallery, name='house_design_gallery'),
    path('project/<int:pk>/attendance/', views.manage_attendance, name='manage_attendance'),
    path('project/<int:pk>/attendance/analysis/', views.attendance_analysis, name='attendance_analysis'),
    path('dashboard/attendance/', views.worker_attendance, name='worker_attendance'),
    path('api/chat/', views.chatbot_api, name='chatbot_api'),
]
