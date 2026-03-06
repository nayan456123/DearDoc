from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from operations.models import Appointment, CareTask, Clinic, Clinician, IntakeRequest, OperationalSignal, Patient, UserProfile


class Command(BaseCommand):
    help = 'Seed the SQLite database with demo telehealth operations data.'

    def handle(self, *args, **options):
        now = timezone.now()

        command_hub, _ = Clinic.objects.update_or_create(
            name='Lucent Command Hub',
            defaults={
                'city': 'Nabha',
                'state': 'Punjab',
                'service_line': 'Acute tele-consultation',
                'bed_capacity': 24,
            },
        )
        south_cluster, _ = Clinic.objects.update_or_create(
            name='Kheda Field Unit',
            defaults={
                'city': 'Patiala',
                'state': 'Punjab',
                'service_line': 'Chronic disease follow-up',
                'bed_capacity': 12,
            },
        )

        user_specs = [
            {
                'username': 'ops.lead',
                'password': 'CommandCenter@123',
                'email': 'ops@lucent.health',
                'display_name': 'Aarav Mehta',
                'role': UserProfile.ROLE_OPS,
                'title': 'Operations Lead',
                'region': 'Punjab North Grid',
            },
            {
                'username': 'doctor.rao',
                'password': 'Doctor@123',
                'email': 'rao@lucent.health',
                'display_name': 'Dr. Isha Rao',
                'role': UserProfile.ROLE_DOCTOR,
                'title': 'Internal Medicine',
                'region': 'Remote Ward A',
            },
            {
                'username': 'doctor.kapoor',
                'password': 'Doctor@123',
                'email': 'kapoor@lucent.health',
                'display_name': 'Dr. Veer Kapoor',
                'role': UserProfile.ROLE_DOCTOR,
                'title': 'Pulmonology',
                'region': 'Remote Ward B',
            },
        ]

        profiles = {}
        for spec in user_specs:
            user, _ = User.objects.update_or_create(
                username=spec['username'],
                defaults={
                    'email': spec['email'],
                    'first_name': spec['display_name'].split()[0],
                    'last_name': ' '.join(spec['display_name'].split()[1:]),
                },
            )
            user.set_password(spec['password'])
            user.save()

            profile, _ = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'display_name': spec['display_name'],
                    'role': spec['role'],
                    'title': spec['title'],
                    'region': spec['region'],
                },
            )
            profiles[spec['username']] = profile

        clinician_rao, _ = Clinician.objects.update_or_create(
            profile=profiles['doctor.rao'],
            defaults={
                'clinic': command_hub,
                'specialty': 'Internal Medicine',
                'license_id': 'PB-IM-4472',
                'languages': 'English, Hindi, Punjabi',
                'consultation_modes': 'Video, Async review',
                'response_sla_hours': 2,
                'next_opening': now + timezone.timedelta(minutes=35),
                'status': Clinician.STATUS_ONLINE,
            },
        )
        clinician_kapoor, _ = Clinician.objects.update_or_create(
            profile=profiles['doctor.kapoor'],
            defaults={
                'clinic': south_cluster,
                'specialty': 'Pulmonology',
                'license_id': 'PB-PU-9921',
                'languages': 'English, Hindi',
                'consultation_modes': 'Video, Field escalation',
                'response_sla_hours': 3,
                'next_opening': now + timezone.timedelta(hours=1, minutes=20),
                'status': Clinician.STATUS_ROUNDING,
            },
        )

        patient_specs = [
            {
                'patient_code': 'LNT-1042',
                'full_name': 'Sunita Bawa',
                'age': 63,
                'sex': 'Female',
                'district': 'Nabha Rural',
                'primary_condition': 'Heart failure decompensation watch',
                'risk_level': Patient.RISK_CRITICAL,
                'device_readiness': Patient.DEVICE_ASSISTED,
                'preferred_language': 'Punjabi',
                'adherence_score': 58,
                'last_vitals_at': now - timezone.timedelta(minutes=18),
                'summary': 'Weight gain of 2.1kg in 72 hours with shortness of breath reported during last village check-in.',
                'clinic': command_hub,
            },
            {
                'patient_code': 'LNT-1027',
                'full_name': 'Harjit Singh',
                'age': 54,
                'sex': 'Male',
                'district': 'Patiala Fringe',
                'primary_condition': 'COPD follow-up',
                'risk_level': Patient.RISK_HIGH,
                'device_readiness': Patient.DEVICE_READY,
                'preferred_language': 'Hindi',
                'adherence_score': 71,
                'last_vitals_at': now - timezone.timedelta(hours=2),
                'summary': 'Recent oxygen saturation dips below target during overnight periods. Requires pulmonary review.',
                'clinic': south_cluster,
            },
            {
                'patient_code': 'LNT-1008',
                'full_name': 'Meena Joshi',
                'age': 39,
                'sex': 'Female',
                'district': 'Sanaur',
                'primary_condition': 'Gestational hypertension follow-up',
                'risk_level': Patient.RISK_HIGH,
                'device_readiness': Patient.DEVICE_ASSISTED,
                'preferred_language': 'Hindi',
                'adherence_score': 82,
                'last_vitals_at': now - timezone.timedelta(minutes=50),
                'summary': 'Two elevated BP readings from assisted kiosk capture. Requires maternal medicine review today.',
                'clinic': command_hub,
            },
            {
                'patient_code': 'LNT-0979',
                'full_name': 'Rakesh Kumar',
                'age': 47,
                'sex': 'Male',
                'district': 'Samana',
                'primary_condition': 'Type II diabetes stabilization',
                'risk_level': Patient.RISK_MODERATE,
                'device_readiness': Patient.DEVICE_READY,
                'preferred_language': 'Punjabi',
                'adherence_score': 88,
                'last_vitals_at': now - timezone.timedelta(hours=6),
                'summary': 'Improving glucose trend but meal logging has fallen off over the last week.',
                'clinic': south_cluster,
            },
            {
                'patient_code': 'LNT-0951',
                'full_name': 'Farzana Ali',
                'age': 31,
                'sex': 'Female',
                'district': 'Nabha Urban',
                'primary_condition': 'Post-partum anemia monitoring',
                'risk_level': Patient.RISK_LOW,
                'device_readiness': Patient.DEVICE_READY,
                'preferred_language': 'Urdu',
                'adherence_score': 91,
                'last_vitals_at': now - timezone.timedelta(days=1, hours=3),
                'summary': 'Stable follow-up track with no current escalation indicators.',
                'clinic': command_hub,
            },
            {
                'patient_code': 'LNT-0914',
                'full_name': 'Gurpreet Kaur',
                'age': 69,
                'sex': 'Female',
                'district': 'Bhawanigarh',
                'primary_condition': 'Stroke rehabilitation pathway',
                'risk_level': Patient.RISK_MODERATE,
                'device_readiness': Patient.DEVICE_OFFLINE,
                'preferred_language': 'Punjabi',
                'adherence_score': 44,
                'last_vitals_at': now - timezone.timedelta(days=2),
                'summary': 'Family unable to complete remote mobility assessment after device battery failure.',
                'clinic': south_cluster,
            },
        ]

        patients = {}
        for spec in patient_specs:
            clinic = spec.pop('clinic')
            patient, _ = Patient.objects.update_or_create(
                patient_code=spec['patient_code'],
                defaults={**spec, 'clinic': clinic},
            )
            patients[patient.patient_code] = patient

        appointment_specs = [
            {
                'patient': patients['LNT-1042'],
                'clinician': clinician_rao,
                'scheduled_for': now + timezone.timedelta(minutes=25),
                'duration_minutes': 25,
                'visit_mode': Appointment.MODE_VIDEO,
                'status': Appointment.STATUS_ACTIVE,
                'queue_label': 'Escalation Bay',
                'briefing': 'Review fluid status and decide on field transfer threshold.',
            },
            {
                'patient': patients['LNT-1008'],
                'clinician': clinician_rao,
                'scheduled_for': now + timezone.timedelta(hours=1, minutes=10),
                'duration_minutes': 20,
                'visit_mode': Appointment.MODE_VIDEO,
                'status': Appointment.STATUS_CONFIRMED,
                'queue_label': 'Maternal Review',
                'briefing': 'Repeat BP review and medication adjustment check.',
            },
            {
                'patient': patients['LNT-1027'],
                'clinician': clinician_kapoor,
                'scheduled_for': now + timezone.timedelta(hours=2),
                'duration_minutes': 30,
                'visit_mode': Appointment.MODE_VIDEO,
                'status': Appointment.STATUS_CONFIRMED,
                'queue_label': 'Respiratory Board',
                'briefing': 'Assess overnight saturation dips and inhaler technique.',
            },
            {
                'patient': patients['LNT-0914'],
                'clinician': clinician_kapoor,
                'scheduled_for': now + timezone.timedelta(hours=6),
                'duration_minutes': 30,
                'visit_mode': Appointment.MODE_FIELD,
                'status': Appointment.STATUS_FOLLOW_UP,
                'queue_label': 'Home Device Recovery',
                'briefing': 'Dispatch assisted rehab check and replace device battery.',
            },
        ]
        for spec in appointment_specs:
            Appointment.objects.update_or_create(
                patient=spec['patient'],
                scheduled_for=spec['scheduled_for'],
                defaults=spec,
            )

        intake_specs = [
            {
                'patient_name': 'Pooja Sharma',
                'age': 42,
                'location': 'Rajpura',
                'channel': 'Village health desk',
                'concern': 'Persistent chest heaviness with dizziness',
                'recommended_pathway': 'Immediate physician review',
                'severity': IntakeRequest.SEVERITY_URGENT,
                'status': IntakeRequest.STATUS_REVIEW,
                'submitted_at': now - timezone.timedelta(minutes=30),
                'assigned_clinician': clinician_rao,
            },
            {
                'patient_name': 'Baldev Singh',
                'age': 61,
                'location': 'Sirhind',
                'channel': 'Nurse callback',
                'concern': 'Missed dialysis transport and rising edema',
                'recommended_pathway': 'Renal coordination',
                'severity': IntakeRequest.SEVERITY_PRIORITY,
                'status': IntakeRequest.STATUS_NEW,
                'submitted_at': now - timezone.timedelta(hours=1, minutes=10),
                'assigned_clinician': clinician_kapoor,
            },
            {
                'patient_name': 'Kiran Gill',
                'age': 27,
                'location': 'Patran',
                'channel': 'Self enrollment',
                'concern': 'Post-discharge wound review',
                'recommended_pathway': 'Async image triage',
                'severity': IntakeRequest.SEVERITY_ROUTINE,
                'status': IntakeRequest.STATUS_SCHEDULED,
                'submitted_at': now - timezone.timedelta(hours=3),
                'assigned_clinician': clinician_rao,
            },
        ]
        for spec in intake_specs:
            IntakeRequest.objects.update_or_create(
                patient_name=spec['patient_name'],
                submitted_at=spec['submitted_at'],
                defaults=spec,
            )

        task_specs = [
            {
                'owner': profiles['ops.lead'],
                'related_patient': patients['LNT-1042'],
                'title': 'Authorize field escalation if edema worsens',
                'summary': 'Keep transfer bed on hold until final clinician decision at 09:30.',
                'due_at': now + timezone.timedelta(minutes=55),
                'status': CareTask.STATUS_PENDING,
                'priority': CareTask.PRIORITY_HIGH,
            },
            {
                'owner': profiles['doctor.rao'],
                'related_patient': patients['LNT-1008'],
                'title': 'Reconcile antihypertensive plan',
                'summary': 'Confirm stock availability with local pharmacy before dosage revision.',
                'due_at': now + timezone.timedelta(hours=2, minutes=30),
                'status': CareTask.STATUS_PENDING,
                'priority': CareTask.PRIORITY_HIGH,
            },
            {
                'owner': profiles['ops.lead'],
                'related_patient': patients['LNT-0914'],
                'title': 'Replace offline rehab kit battery',
                'summary': 'Technician slot missed yesterday; rebook field runner and notify caregiver.',
                'due_at': now - timezone.timedelta(minutes=25),
                'status': CareTask.STATUS_PENDING,
                'priority': CareTask.PRIORITY_MEDIUM,
            },
            {
                'owner': profiles['doctor.kapoor'],
                'related_patient': patients['LNT-1027'],
                'title': 'Validate nocturnal oxygen trend',
                'summary': 'Review uploaded overnight trace before pulmonary round begins.',
                'due_at': now + timezone.timedelta(hours=1, minutes=40),
                'status': CareTask.STATUS_BLOCKED,
                'priority': CareTask.PRIORITY_MEDIUM,
            },
        ]
        for spec in task_specs:
            CareTask.objects.update_or_create(title=spec['title'], defaults=spec)

        signal_specs = [
            {
                'title': 'Critical device adherence drop',
                'detail': 'Six high-risk households have not uploaded vitals in the last 48 hours.',
                'source': 'Remote Monitoring',
                'severity': OperationalSignal.SEVERITY_CRITICAL,
                'opened_at': now - timezone.timedelta(minutes=12),
                'acknowledged': False,
            },
            {
                'title': 'Bandwidth degradation across east cluster',
                'detail': 'Video consults may downgrade to audio-first workflow until 11:00.',
                'source': 'Network Operations',
                'severity': OperationalSignal.SEVERITY_WATCH,
                'opened_at': now - timezone.timedelta(minutes=38),
                'acknowledged': False,
            },
            {
                'title': 'Maternal review lane cleared',
                'detail': 'Backlog reduced below two-hour target after overnight catch-up.',
                'source': 'Scheduling',
                'severity': OperationalSignal.SEVERITY_INFO,
                'opened_at': now - timezone.timedelta(hours=2),
                'acknowledged': True,
            },
        ]
        for spec in signal_specs:
            OperationalSignal.objects.update_or_create(title=spec['title'], defaults=spec)

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
