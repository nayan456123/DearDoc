from rest_framework import serializers

from .models import Appointment, CareTask, Clinic, Clinician, IntakeRequest, OperationalSignal, Patient, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'display_name', 'role', 'title', 'region']


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'city', 'state', 'service_line', 'bed_capacity']


class ClinicianSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    clinic = ClinicSerializer()

    class Meta:
        model = Clinician
        fields = [
            'id',
            'profile',
            'clinic',
            'specialty',
            'license_id',
            'languages',
            'consultation_modes',
            'response_sla_hours',
            'next_opening',
            'status',
        ]


class PatientSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer()

    class Meta:
        model = Patient
        fields = [
            'id',
            'clinic',
            'full_name',
            'patient_code',
            'age',
            'sex',
            'district',
            'primary_condition',
            'risk_level',
            'device_readiness',
            'preferred_language',
            'adherence_score',
            'last_vitals_at',
            'summary',
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    clinician = ClinicianSerializer()

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'clinician',
            'scheduled_for',
            'duration_minutes',
            'visit_mode',
            'status',
            'queue_label',
            'briefing',
        ]


class IntakeRequestSerializer(serializers.ModelSerializer):
    assigned_clinician = ClinicianSerializer()

    class Meta:
        model = IntakeRequest
        fields = [
            'id',
            'patient_name',
            'age',
            'location',
            'channel',
            'concern',
            'recommended_pathway',
            'severity',
            'status',
            'submitted_at',
            'assigned_clinician',
        ]


class CareTaskSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer()
    related_patient = PatientSerializer()

    class Meta:
        model = CareTask
        fields = ['id', 'owner', 'related_patient', 'title', 'summary', 'due_at', 'status', 'priority']


class OperationalSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalSignal
        fields = ['id', 'title', 'detail', 'source', 'severity', 'opened_at', 'acknowledged']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareTask
        fields = ['status']


class IntakeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntakeRequest
        fields = ['status']
