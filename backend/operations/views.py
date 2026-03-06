from django.db.models import Case, Count, When
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment, CareTask, Clinician, IntakeRequest, OperationalSignal, Patient, UserProfile
from .serializers import (
    AppointmentSerializer,
    CareTaskSerializer,
    ClinicianSerializer,
    IntakeRequestSerializer,
    IntakeStatusSerializer,
    LoginSerializer,
    OperationalSignalSerializer,
    PatientSerializer,
    TaskStatusSerializer,
    UserProfileSerializer,
)


def ensure_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'display_name': user.get_full_name() or user.username,
            'role': UserProfile.ROLE_PATIENT,
        },
    )
    return profile


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserProfileSerializer(ensure_profile(user)).data})


class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserProfileSerializer(ensure_profile(request.user)).data)


class DashboardView(APIView):
    def get(self, request):
        now = timezone.now()
        upcoming_window = now + timezone.timedelta(hours=24)

        summary = {
            'activePatients': Patient.objects.count(),
            'criticalWatchlist': Patient.objects.filter(
                risk_level__in=[Patient.RISK_HIGH, Patient.RISK_CRITICAL]
            ).count(),
            'appointmentsNext24h': Appointment.objects.filter(
                scheduled_for__gte=now,
                scheduled_for__lte=upcoming_window,
            ).count(),
            'intakeBacklog': IntakeRequest.objects.filter(
                status__in=[IntakeRequest.STATUS_NEW, IntakeRequest.STATUS_REVIEW]
            ).count(),
            'slaBreaches': CareTask.objects.filter(
                status=CareTask.STATUS_PENDING,
                due_at__lt=now,
            ).count(),
            'coverageOnline': Clinician.objects.filter(status=Clinician.STATUS_ONLINE).count(),
        }

        risk_mix = list(
            Patient.objects.values('risk_level').annotate(total=Count('id')).order_by('-total')
        )

        appointments = Appointment.objects.select_related(
            'patient',
            'patient__clinic',
            'clinician',
            'clinician__clinic',
            'clinician__profile',
            'clinician__profile__user',
        ).order_by('scheduled_for')[:6]
        patients = Patient.objects.select_related('clinic').order_by(
            Case(
                When(risk_level=Patient.RISK_CRITICAL, then=0),
                When(risk_level=Patient.RISK_HIGH, then=1),
                When(risk_level=Patient.RISK_MODERATE, then=2),
                default=3,
            ),
            '-last_vitals_at',
        )[:6]
        intake = IntakeRequest.objects.select_related(
            'assigned_clinician',
            'assigned_clinician__clinic',
            'assigned_clinician__profile',
            'assigned_clinician__profile__user',
        ).order_by('submitted_at')[:5]
        tasks = CareTask.objects.select_related(
            'owner',
            'owner__user',
            'related_patient',
            'related_patient__clinic',
        ).order_by('due_at')[:6]
        network = Clinician.objects.select_related(
            'profile',
            'profile__user',
            'clinic',
        ).order_by('next_opening')[:5]
        signals = OperationalSignal.objects.order_by('-opened_at')[:4]

        return Response(
            {
                'user': UserProfileSerializer(ensure_profile(request.user)).data,
                'summary': summary,
                'riskMix': risk_mix,
                'signals': OperationalSignalSerializer(signals, many=True).data,
                'appointments': AppointmentSerializer(appointments, many=True).data,
                'patients': PatientSerializer(patients, many=True).data,
                'intake': IntakeRequestSerializer(intake, many=True).data,
                'tasks': CareTaskSerializer(tasks, many=True).data,
                'network': ClinicianSerializer(network, many=True).data,
            }
        )


class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.select_related('clinic').order_by('full_name')


class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.select_related(
            'patient',
            'patient__clinic',
            'clinician',
            'clinician__clinic',
            'clinician__profile',
            'clinician__profile__user',
        ).order_by('scheduled_for')


class ClinicianListView(generics.ListAPIView):
    serializer_class = ClinicianSerializer

    def get_queryset(self):
        return Clinician.objects.select_related('profile', 'profile__user', 'clinic').order_by(
            'profile__display_name'
        )


class IntakeListView(generics.ListAPIView):
    serializer_class = IntakeRequestSerializer

    def get_queryset(self):
        return IntakeRequest.objects.select_related(
            'assigned_clinician',
            'assigned_clinician__clinic',
            'assigned_clinician__profile',
            'assigned_clinician__profile__user',
        ).order_by('submitted_at')


class TaskListView(generics.ListAPIView):
    serializer_class = CareTaskSerializer

    def get_queryset(self):
        return CareTask.objects.select_related(
            'owner',
            'owner__user',
            'related_patient',
            'related_patient__clinic',
        ).order_by('due_at')


class TaskDetailView(generics.UpdateAPIView):
    queryset = CareTask.objects.all()
    serializer_class = TaskStatusSerializer


class IntakeDetailView(generics.UpdateAPIView):
    queryset = IntakeRequest.objects.all()
    serializer_class = IntakeStatusSerializer
