from rest_framework import serializers

from .models import Appointment, AvailabilitySlot, CallSignal, DoctorProfile, PatientProfile, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'display_name', 'role', 'headline']


class DoctorProfileSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()

    class Meta:
        model = DoctorProfile
        fields = ['id', 'user_profile', 'specialty', 'bio', 'years_experience', 'room_label']


class PatientProfileSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()

    class Meta:
        model = PatientProfile
        fields = ['id', 'user_profile', 'age', 'location', 'primary_goal', 'emergency_contact']


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer()

    class Meta:
        model = AvailabilitySlot
        fields = ['id', 'doctor', 'starts_at', 'ends_at', 'status', 'visit_mode', 'label']


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer()
    patient = PatientProfileSerializer()
    slot = AvailabilitySlotSerializer(allow_null=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor',
            'patient',
            'slot',
            'starts_at',
            'ends_at',
            'status',
            'concern',
            'symptoms',
            'patient_notes',
            'urgency',
            'triage_score',
            'copilot_summary',
            'copilot_checklist',
            'innovation_tag',
            'meeting_code',
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class SlotCreateSerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField()
    visit_mode = serializers.ChoiceField(choices=AvailabilitySlot.MODE_CHOICES, default=AvailabilitySlot.MODE_VIDEO)
    label = serializers.CharField(max_length=80, allow_blank=True, required=False)


class TriagePreviewSerializer(serializers.Serializer):
    concern = serializers.CharField(max_length=180)
    symptoms = serializers.CharField()
    notes = serializers.CharField(allow_blank=True, required=False)


class AppointmentRequestSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()
    concern = serializers.CharField(max_length=180)
    symptoms = serializers.CharField()
    patient_notes = serializers.CharField(allow_blank=True, required=False)


class AppointmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)


class CallSignalWriteSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=CallSignal.KIND_CHOICES)
    payload = serializers.JSONField(required=False)
