from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_OPS = 'ops'
    ROLE_DOCTOR = 'doctor'
    ROLE_PATIENT = 'patient'
    ROLE_CHOICES = [
        (ROLE_OPS, 'Operations'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=120)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    title = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.display_name


class Clinic(models.Model):
    name = models.CharField(max_length=140)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    service_line = models.CharField(max_length=120)
    bed_capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Clinician(models.Model):
    STATUS_ONLINE = 'online'
    STATUS_ROUNDING = 'rounding'
    STATUS_OFFLINE = 'offline'
    STATUS_CHOICES = [
        (STATUS_ONLINE, 'Online'),
        (STATUS_ROUNDING, 'Rounding'),
        (STATUS_OFFLINE, 'Offline'),
    ]

    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='clinician')
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, related_name='clinicians')
    specialty = models.CharField(max_length=120)
    license_id = models.CharField(max_length=80)
    languages = models.CharField(max_length=200)
    consultation_modes = models.CharField(max_length=120)
    response_sla_hours = models.PositiveIntegerField(default=4)
    next_opening = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ONLINE)

    def __str__(self):
        return self.profile.display_name


class Patient(models.Model):
    RISK_LOW = 'low'
    RISK_MODERATE = 'moderate'
    RISK_HIGH = 'high'
    RISK_CRITICAL = 'critical'
    RISK_CHOICES = [
        (RISK_LOW, 'Low'),
        (RISK_MODERATE, 'Moderate'),
        (RISK_HIGH, 'High'),
        (RISK_CRITICAL, 'Critical'),
    ]

    DEVICE_READY = 'ready'
    DEVICE_ASSISTED = 'assisted'
    DEVICE_OFFLINE = 'offline'
    DEVICE_CHOICES = [
        (DEVICE_READY, 'Ready'),
        (DEVICE_ASSISTED, 'Assisted'),
        (DEVICE_OFFLINE, 'Offline'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, related_name='patients')
    full_name = models.CharField(max_length=120)
    patient_code = models.CharField(max_length=20, unique=True)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=20)
    district = models.CharField(max_length=120)
    primary_condition = models.CharField(max_length=160)
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default=RISK_LOW)
    device_readiness = models.CharField(max_length=20, choices=DEVICE_CHOICES, default=DEVICE_READY)
    preferred_language = models.CharField(max_length=80)
    adherence_score = models.PositiveIntegerField(default=0)
    last_vitals_at = models.DateTimeField()
    summary = models.TextField()

    def __str__(self):
        return f'{self.patient_code} - {self.full_name}'


class IntakeRequest(models.Model):
    SEVERITY_ROUTINE = 'routine'
    SEVERITY_PRIORITY = 'priority'
    SEVERITY_URGENT = 'urgent'
    SEVERITY_CHOICES = [
        (SEVERITY_ROUTINE, 'Routine'),
        (SEVERITY_PRIORITY, 'Priority'),
        (SEVERITY_URGENT, 'Urgent'),
    ]

    STATUS_NEW = 'new'
    STATUS_REVIEW = 'review'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_DECLINED = 'declined'
    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_REVIEW, 'In Review'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_DECLINED, 'Declined'),
    ]

    patient_name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    location = models.CharField(max_length=120)
    channel = models.CharField(max_length=80)
    concern = models.CharField(max_length=200)
    recommended_pathway = models.CharField(max_length=120)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_ROUTINE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    submitted_at = models.DateTimeField()
    assigned_clinician = models.ForeignKey(
        Clinician,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='intake_requests',
    )

    def __str__(self):
        return self.patient_name


class Appointment(models.Model):
    MODE_VIDEO = 'video'
    MODE_ASYNC = 'async'
    MODE_FIELD = 'field'
    MODE_CHOICES = [
        (MODE_VIDEO, 'Video'),
        (MODE_ASYNC, 'Async'),
        (MODE_FIELD, 'Field'),
    ]

    STATUS_TRIAGE = 'triage'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_ACTIVE = 'active'
    STATUS_FOLLOW_UP = 'follow_up'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_TRIAGE, 'Triage'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_FOLLOW_UP, 'Follow-up'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    clinician = models.ForeignKey(Clinician, on_delete=models.SET_NULL, null=True, related_name='appointments')
    scheduled_for = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=20)
    visit_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_VIDEO)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    queue_label = models.CharField(max_length=80)
    briefing = models.TextField()

    def __str__(self):
        return f'{self.patient.full_name} @ {self.scheduled_for}'


class CareTask(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_BLOCKED = 'blocked'
    STATUS_DONE = 'done'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_BLOCKED, 'Blocked'),
        (STATUS_DONE, 'Done'),
    ]

    PRIORITY_HIGH = 'high'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_LOW = 'low'
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_LOW, 'Low'),
    ]

    owner = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='tasks')
    related_patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )
    title = models.CharField(max_length=160)
    summary = models.TextField()
    due_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)

    def __str__(self):
        return self.title


class OperationalSignal(models.Model):
    SEVERITY_INFO = 'info'
    SEVERITY_WATCH = 'watch'
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_CHOICES = [
        (SEVERITY_INFO, 'Info'),
        (SEVERITY_WATCH, 'Watch'),
        (SEVERITY_CRITICAL, 'Critical'),
    ]

    title = models.CharField(max_length=160)
    detail = models.TextField()
    source = models.CharField(max_length=120)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_INFO)
    opened_at = models.DateTimeField()
    acknowledged = models.BooleanField(default=False)

    def __str__(self):
        return self.title
