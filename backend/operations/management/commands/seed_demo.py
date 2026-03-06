from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from operations.models import Appointment, AvailabilitySlot, DoctorProfile, PatientProfile, UserProfile
from operations.views import get_triage_bundle


class Command(BaseCommand):
    help = 'Seed demo doctor/patient data for the local-first hackathon build.'

    def handle(self, *args, **options):
        now = timezone.now()

        doctor_user, _ = User.objects.update_or_create(
            username='doctor.rao',
            defaults={'first_name': 'Isha', 'last_name': 'Rao', 'email': 'doctor@lucent.local'},
        )
        doctor_user.set_password('Doctor@123')
        doctor_user.save()
        doctor_profile, _ = UserProfile.objects.update_or_create(
            user=doctor_user,
            defaults={
                'display_name': 'Dr. Isha Rao',
                'role': UserProfile.ROLE_DOCTOR,
                'headline': 'Cardio-respiratory telehealth lead',
            },
        )
        doctor_detail, _ = DoctorProfile.objects.update_or_create(
            user_profile=doctor_profile,
            defaults={
                'specialty': 'Internal Medicine',
                'bio': 'Runs fast remote consults, review sessions, and follow-up video care for urgent outpatient issues.',
                'years_experience': 9,
                'room_label': 'LUCENT-ROOM-A',
            },
        )

        patient_specs = [
            {
                'username': 'patient.asha',
                'password': 'Patient@123',
                'display_name': 'Asha Singh',
                'age': 27,
                'location': 'Patiala',
                'primary_goal': 'Fast respiratory consult',
                'emergency_contact': '+91 90000 11111',
            },
            {
                'username': 'patient.rohan',
                'password': 'Patient@123',
                'display_name': 'Rohan Mehta',
                'age': 34,
                'location': 'Nabha',
                'primary_goal': 'Chest pain follow-up',
                'emergency_contact': '+91 90000 22222',
            },
        ]

        patient_profiles = {}
        for spec in patient_specs:
            user, _ = User.objects.update_or_create(
                username=spec['username'],
                defaults={'first_name': spec['display_name'].split()[0], 'last_name': spec['display_name'].split()[-1]},
            )
            user.set_password(spec['password'])
            user.save()
            profile, _ = UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'display_name': spec['display_name'],
                    'role': UserProfile.ROLE_PATIENT,
                    'headline': 'Hackathon demo patient',
                },
            )
            patient, _ = PatientProfile.objects.update_or_create(
                user_profile=profile,
                defaults={
                    'age': spec['age'],
                    'location': spec['location'],
                    'primary_goal': spec['primary_goal'],
                    'emergency_contact': spec['emergency_contact'],
                },
            )
            patient_profiles[spec['username']] = patient

        slots = []
        for index, hours in enumerate([2, 4, 6, 24, 26]):
            slot, _ = AvailabilitySlot.objects.update_or_create(
                doctor=doctor_detail,
                starts_at=now + timezone.timedelta(hours=hours),
                defaults={
                    'ends_at': now + timezone.timedelta(hours=hours, minutes=30),
                    'status': AvailabilitySlot.STATUS_OPEN if index > 1 else AvailabilitySlot.STATUS_BOOKED,
                    'visit_mode': AvailabilitySlot.MODE_VIDEO,
                    'label': 'Express video consult' if index < 3 else 'Follow-up lane',
                },
            )
            slots.append(slot)

        appointment_specs = [
            {
                'patient': patient_profiles['patient.asha'],
                'slot': slots[0],
                'concern': 'Shortness of breath after fever',
                'symptoms': 'Mild cough, breathlessness climbing stairs, fever since yesterday.',
                'patient_notes': 'Would like the earliest slot available.',
                'status': Appointment.STATUS_REQUESTED,
            },
            {
                'patient': patient_profiles['patient.rohan'],
                'slot': slots[1],
                'concern': 'Recurring chest tightness',
                'symptoms': 'Tightness in chest at night, mild dizziness, previous episode two weeks ago.',
                'patient_notes': 'Have previous prescription notes ready.',
                'status': Appointment.STATUS_CONFIRMED,
            },
        ]

        for spec in appointment_specs:
            bundle = get_triage_bundle(spec['concern'], spec['symptoms'], spec['patient_notes'])
            Appointment.objects.update_or_create(
                patient=spec['patient'],
                doctor=doctor_detail,
                starts_at=spec['slot'].starts_at,
                defaults={
                    'slot': spec['slot'],
                    'ends_at': spec['slot'].ends_at,
                    'status': spec['status'],
                    'concern': spec['concern'],
                    'symptoms': spec['symptoms'],
                    'patient_notes': spec['patient_notes'],
                    'urgency': bundle['urgency'],
                    'triage_score': bundle['triage_score'],
                    'copilot_summary': bundle['summary'],
                    'copilot_checklist': bundle['checklist'],
                    'meeting_code': f'meet-{spec["patient"].id}-{spec["slot"].id}',
                },
            )

        self.stdout.write(self.style.SUCCESS('Doctor/patient demo seeded.'))
