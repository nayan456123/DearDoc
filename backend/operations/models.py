from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'
    ROLE_CHOICES = [
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=120)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    headline = models.CharField(max_length=140, blank=True)

    def __str__(self):
        return f'{self.display_name} ({self.role})'


class DoctorProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=120)
    bio = models.TextField()
    years_experience = models.PositiveIntegerField(default=0)
    room_label = models.CharField(max_length=80)

    def __str__(self):
        return self.user_profile.display_name


class PatientProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(default=18)
    location = models.CharField(max_length=120)
    primary_goal = models.CharField(max_length=160)
    emergency_contact = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.user_profile.display_name


class AvailabilitySlot(models.Model):
    STATUS_OPEN = 'open'
    STATUS_BOOKED = 'booked'
    STATUS_BLOCKED = 'blocked'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_BOOKED, 'Booked'),
        (STATUS_BLOCKED, 'Blocked'),
    ]

    MODE_VIDEO = 'video'
    MODE_AUDIO = 'audio'
    MODE_CHOICES = [
        (MODE_VIDEO, 'Video'),
        (MODE_AUDIO, 'Audio'),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability_slots')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    visit_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_VIDEO)
    label = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ['starts_at']

    def __str__(self):
        return f'{self.doctor.user_profile.display_name} {self.starts_at}'


class Appointment(models.Model):
    STATUS_REQUESTED = 'requested'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_LIVE = 'live'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'Requested'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_LIVE, 'Live'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    URGENCY_LOW = 'low'
    URGENCY_MEDIUM = 'medium'
    URGENCY_HIGH = 'high'
    URGENCY_CHOICES = [
        (URGENCY_LOW, 'Low'),
        (URGENCY_MEDIUM, 'Medium'),
        (URGENCY_HIGH, 'High'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment',
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    concern = models.CharField(max_length=180)
    symptoms = models.TextField()
    patient_notes = models.TextField(blank=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default=URGENCY_LOW)
    triage_score = models.PositiveIntegerField(default=0)
    copilot_summary = models.TextField()
    copilot_checklist = models.JSONField(default=list, blank=True)
    innovation_tag = models.CharField(max_length=120, default='PulseMatch Copilot')
    meeting_code = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ['starts_at']

    def __str__(self):
        return f'{self.patient.user_profile.display_name} with {self.doctor.user_profile.display_name}'


class CallSignal(models.Model):
    KIND_OFFER = 'offer'
    KIND_ANSWER = 'answer'
    KIND_CANDIDATE = 'candidate'
    KIND_READY = 'ready'
    KIND_END = 'end'
    KIND_CHOICES = [
        (KIND_OFFER, 'Offer'),
        (KIND_ANSWER, 'Answer'),
        (KIND_CANDIDATE, 'Candidate'),
        (KIND_READY, 'Ready'),
        (KIND_END, 'End'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='signals')
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_signals')
    recipient_role = models.CharField(max_length=20, choices=UserProfile.ROLE_CHOICES)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.kind} -> {self.recipient_role}'
