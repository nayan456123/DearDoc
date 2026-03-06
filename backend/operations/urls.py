from django.urls import path

from .views import (
    AppointmentListView,
    ClinicianListView,
    DashboardView,
    IntakeDetailView,
    IntakeListView,
    LoginView,
    LogoutView,
    MeView,
    PatientListView,
    TaskDetailView,
    TaskListView,
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('overview/', DashboardView.as_view(), name='overview'),
    path('patients/', PatientListView.as_view(), name='patients'),
    path('appointments/', AppointmentListView.as_view(), name='appointments'),
    path('clinicians/', ClinicianListView.as_view(), name='clinicians'),
    path('intake/', IntakeListView.as_view(), name='intake'),
    path('intake/<int:pk>/', IntakeDetailView.as_view(), name='intake-detail'),
    path('tasks/', TaskListView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
]
