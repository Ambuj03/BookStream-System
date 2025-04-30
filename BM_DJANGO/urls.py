"""
URL configuration for BM_DJANGO project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from bm_app.admin import mark_notification_read_view
from bm_app.views import admin_notifications_view
from django.contrib.admin.views.decorators import staff_member_required
from bm_app import admin_views
from bm_app.profile_view import ResetPasswordView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/notifications/', admin_notifications_view, name='admin_notifications'),
    path('admin/notifications/mark-read/<int:notification_id>/', mark_notification_read_view, name='mark_notification_read'),
    
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),

    path('admin/api/monthly-distribution-data/', admin_views.get_monthly_distribution_data, name='monthly_distribution_data'),
    path('admin/api/top-distributors-data/', admin_views.get_top_distributors, name='top_distributors_data'),
    path('admin/api/top-categories-data/', admin_views.get_top_categories, name='top_categories_data'),
    path('admin/api/revenue-data/', admin_views.get_revenue_data, name='revenue_data'),

    path('admin/', admin.site.urls),
    path('',include('bm_app.urls')),

    #For passwordReset
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='bm_app/pass_reset/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='bm_app/pass_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='bm_app/pass_reset/password_reset_complete.html'), name='password_reset_complete'),

]
