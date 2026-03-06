from django.urls import path

from .views import (
    AppointmentDetailView,
    AppointmentListView,
    AppointmentRequestView,
    AppointmentStatusView,
    CallSignalView,
    DoctorDashboardView,
    LoginView,
    LogoutView,
    MeView,
    PatientDashboardView,
    SlotListCreateView,
    TriagePreviewView,
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('doctor/dashboard/', DoctorDashboardView.as_view(), name='doctor-dashboard'),
    path('patient/dashboard/', PatientDashboardView.as_view(), name='patient-dashboard'),
    path('triage/preview/', TriagePreviewView.as_view(), name='triage-preview'),
    path('slots/', SlotListCreateView.as_view(), name='slots'),
    path('appointments/', AppointmentListView.as_view(), name='appointments'),
    path('appointments/request/', AppointmentRequestView.as_view(), name='appointment-request'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/status/', AppointmentStatusView.as_view(), name='appointment-status'),
    path('appointments/<int:pk>/signals/', CallSignalView.as_view(), name='appointment-signals'),
]
