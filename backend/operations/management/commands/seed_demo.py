from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from operations.models import Appointment, AvailabilitySlot, CallSignal, DoctorProfile, PatientProfile, UserProfile


class Command(BaseCommand):
    help = 'Seed only the demo doctor/patient accounts for the local-first build.'

    def handle(self, *args, **options):
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
        DoctorProfile.objects.update_or_create(
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
                    'headline': '',
                },
            )
            PatientProfile.objects.update_or_create(
                user_profile=profile,
                defaults={
                    'age': spec['age'],
                    'location': spec['location'],
                    'primary_goal': spec['primary_goal'],
                    'emergency_contact': spec['emergency_contact'],
                },
            )

        CallSignal.objects.all().delete()
        Appointment.objects.all().delete()
        AvailabilitySlot.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Demo accounts seeded with no dummy appointments or slots.'))
