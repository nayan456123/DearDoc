from uuid import uuid4

from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment, AvailabilitySlot, CallSignal, DoctorProfile, PatientProfile, UserProfile
from .serializers import (
    AppointmentRequestSerializer,
    AppointmentSerializer,
    AppointmentStatusSerializer,
    AvailabilitySlotSerializer,
    CallSignalWriteSerializer,
    DoctorProfileSerializer,
    LoginSerializer,
    SlotCreateSerializer,
    TriagePreviewSerializer,
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


def require_role(request, role):
    profile = ensure_profile(request.user)
    if profile.role != role:
        return None, Response({'detail': 'You do not have access to this area.'}, status=403)
    return profile, None


def get_triage_bundle(concern, symptoms, notes=''):
    text = f'{concern} {symptoms} {notes}'.lower()
    score = 28
    checklist = ['Keep camera and microphone ready for the call.']
    tags = []

    urgent_terms = {
        'chest': 28,
        'breath': 22,
        'bleeding': 30,
        'severe': 18,
        'collapse': 35,
        'faint': 24,
        'pain': 12,
    }
    moderate_terms = {
        'fever': 10,
        'cough': 10,
        'infection': 14,
        'anxiety': 9,
        'rash': 8,
        'sleep': 6,
        'migraine': 8,
    }

    for keyword, weight in urgent_terms.items():
        if keyword in text:
            score += weight
            tags.append(keyword)

    for keyword, weight in moderate_terms.items():
        if keyword in text:
            score += weight
            tags.append(keyword)

    if score >= 70:
        urgency = Appointment.URGENCY_HIGH
        checklist.extend(
            [
                'Keep a family member nearby during the consultation if possible.',
                'Note the exact time the symptoms began.',
            ]
        )
    elif score >= 48:
        urgency = Appointment.URGENCY_MEDIUM
        checklist.extend(
            [
                'Prepare any medicines you are currently taking.',
                'Write down the top three symptom changes from the last 24 hours.',
            ]
        )
    else:
        urgency = Appointment.URGENCY_LOW
        checklist.append('Prepare one short summary of what you want help with today.')

    if 'sleep' in text or 'stress' in text:
        specialty_hint = 'General medicine with wellbeing follow-up'
    elif 'breath' in text or 'cough' in text:
        specialty_hint = 'Respiratory review'
    elif 'pain' in text or 'chest' in text:
        specialty_hint = 'Priority medical review'
    else:
        specialty_hint = 'Primary consult'

    summary = (
        f'PulseMatch Copilot marked this request as {urgency}. '
        f'Likely consult lane: {specialty_hint}. '
        f'Key signals detected: {", ".join(tags[:4]) if tags else "general symptoms"}.'
    )

    return {
        'urgency': urgency,
        'triage_score': min(score, 100),
        'summary': summary,
        'checklist': checklist,
        'specialty_hint': specialty_hint,
    }


def serialize_slots(queryset):
    return AvailabilitySlotSerializer(queryset, many=True).data


def get_doctor_dashboard(profile):
    doctor = profile.doctor_profile
    appointments = Appointment.objects.select_related(
        'patient',
        'patient__user_profile',
        'doctor',
        'doctor__user_profile',
        'slot',
    ).filter(doctor=doctor)
    slots = AvailabilitySlot.objects.select_related('doctor', 'doctor__user_profile').filter(doctor=doctor)

    return {
        'profile': DoctorProfileSerializer(doctor).data,
        'stats': {
            'bookedToday': appointments.filter(starts_at__date=timezone.localdate()).count(),
            'waitingRequests': appointments.filter(status=Appointment.STATUS_REQUESTED).count(),
            'liveNow': appointments.filter(status=Appointment.STATUS_LIVE).count(),
            'openSlots': slots.filter(status=AvailabilitySlot.STATUS_OPEN).count(),
        },
        'appointments': AppointmentSerializer(appointments.order_by('starts_at'), many=True).data,
        'slots': serialize_slots(slots.order_by('starts_at')),
        'kanban': list(appointments.values('status').annotate(total=Count('id')).order_by('status')),
    }


def get_patient_dashboard(profile):
    patient = profile.patient_profile
    appointments = Appointment.objects.select_related(
        'patient',
        'patient__user_profile',
        'doctor',
        'doctor__user_profile',
        'slot',
    ).filter(patient=patient)
    slots = AvailabilitySlot.objects.select_related('doctor', 'doctor__user_profile').filter(
        status=AvailabilitySlot.STATUS_OPEN,
        starts_at__gte=timezone.now(),
    )[:12]

    doctor = DoctorProfile.objects.select_related('user_profile').first()

    return {
        'profile': {
            **UserProfileSerializer(profile).data,
            'age': patient.age,
            'location': patient.location,
            'primary_goal': patient.primary_goal,
        },
        'doctorSpotlight': DoctorProfileSerializer(doctor).data if doctor else None,
        'appointments': AppointmentSerializer(appointments.order_by('starts_at'), many=True).data,
        'availableSlots': serialize_slots(slots),
    }


def can_access_appointment(profile, appointment):
    if profile.role == UserProfile.ROLE_DOCTOR:
        return hasattr(profile, 'doctor_profile') and appointment.doctor_id == profile.doctor_profile.id
    return hasattr(profile, 'patient_profile') and appointment.patient_id == profile.patient_profile.id


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
        profile = ensure_profile(user)
        payload = {'token': token.key, 'user': UserProfileSerializer(profile).data}
        payload['dashboard'] = (
            get_doctor_dashboard(profile)
            if profile.role == UserProfile.ROLE_DOCTOR
            else get_patient_dashboard(profile)
        )
        return Response(payload)


class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        profile = ensure_profile(request.user)
        payload = {'user': UserProfileSerializer(profile).data}
        payload['dashboard'] = (
            get_doctor_dashboard(profile)
            if profile.role == UserProfile.ROLE_DOCTOR
            else get_patient_dashboard(profile)
        )
        return Response(payload)


class TriagePreviewView(APIView):
    def post(self, request):
        profile = ensure_profile(request.user)
        if profile.role != UserProfile.ROLE_PATIENT:
            return Response({'detail': 'Only patients can request a preview.'}, status=403)

        serializer = TriagePreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bundle = get_triage_bundle(
            serializer.validated_data['concern'],
            serializer.validated_data['symptoms'],
            serializer.validated_data.get('notes', ''),
        )
        suggested_slots = AvailabilitySlot.objects.select_related('doctor', 'doctor__user_profile').filter(
            status=AvailabilitySlot.STATUS_OPEN,
            starts_at__gte=timezone.now(),
        )[:3]
        return Response({**bundle, 'suggestedSlots': serialize_slots(suggested_slots)})


class DoctorDashboardView(APIView):
    def get(self, request):
        profile, error = require_role(request, UserProfile.ROLE_DOCTOR)
        if error:
            return error
        return Response(get_doctor_dashboard(profile))


class PatientDashboardView(APIView):
    def get(self, request):
        profile, error = require_role(request, UserProfile.ROLE_PATIENT)
        if error:
            return error
        return Response(get_patient_dashboard(profile))


class SlotListCreateView(APIView):
    def get(self, request):
        profile = ensure_profile(request.user)
        if profile.role == UserProfile.ROLE_DOCTOR:
            slots = AvailabilitySlot.objects.select_related('doctor', 'doctor__user_profile').filter(
                doctor=profile.doctor_profile
            )
        else:
            slots = AvailabilitySlot.objects.select_related('doctor', 'doctor__user_profile').filter(
                status=AvailabilitySlot.STATUS_OPEN,
                starts_at__gte=timezone.now(),
            )
        return Response(serialize_slots(slots.order_by('starts_at')))

    def post(self, request):
        profile, error = require_role(request, UserProfile.ROLE_DOCTOR)
        if error:
            return error

        serializer = SlotCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = AvailabilitySlot.objects.create(
            doctor=profile.doctor_profile,
            starts_at=serializer.validated_data['starts_at'],
            ends_at=serializer.validated_data['ends_at'],
            visit_mode=serializer.validated_data['visit_mode'],
            label=serializer.validated_data.get('label', ''),
        )
        return Response(AvailabilitySlotSerializer(slot).data, status=201)


class AppointmentRequestView(APIView):
    def post(self, request):
        profile, error = require_role(request, UserProfile.ROLE_PATIENT)
        if error:
            return error

        serializer = AppointmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            slot = AvailabilitySlot.objects.select_for_update().select_related(
                'doctor',
                'doctor__user_profile',
            ).get(id=serializer.validated_data['slot_id'])

            if slot.status != AvailabilitySlot.STATUS_OPEN:
                return Response({'detail': 'That slot is no longer available.'}, status=400)

            bundle = get_triage_bundle(
                serializer.validated_data['concern'],
                serializer.validated_data['symptoms'],
                serializer.validated_data.get('patient_notes', ''),
            )

            appointment = Appointment.objects.create(
                patient=profile.patient_profile,
                doctor=slot.doctor,
                slot=slot,
                starts_at=slot.starts_at,
                ends_at=slot.ends_at,
                status=Appointment.STATUS_REQUESTED,
                concern=serializer.validated_data['concern'],
                symptoms=serializer.validated_data['symptoms'],
                patient_notes=serializer.validated_data.get('patient_notes', ''),
                urgency=bundle['urgency'],
                triage_score=bundle['triage_score'],
                copilot_summary=bundle['summary'],
                copilot_checklist=bundle['checklist'],
                meeting_code=uuid4().hex[:10],
            )
            slot.status = AvailabilitySlot.STATUS_BOOKED
            slot.save(update_fields=['status'])

        return Response(AppointmentSerializer(appointment).data, status=201)


class AppointmentListView(APIView):
    def get(self, request):
        profile = ensure_profile(request.user)
        if profile.role == UserProfile.ROLE_DOCTOR:
            appointments = Appointment.objects.select_related(
                'patient',
                'patient__user_profile',
                'doctor',
                'doctor__user_profile',
                'slot',
            ).filter(doctor=profile.doctor_profile)
        else:
            appointments = Appointment.objects.select_related(
                'patient',
                'patient__user_profile',
                'doctor',
                'doctor__user_profile',
                'slot',
            ).filter(patient=profile.patient_profile)
        return Response(AppointmentSerializer(appointments.order_by('starts_at'), many=True).data)


class AppointmentDetailView(APIView):
    def get(self, request, pk):
        profile = ensure_profile(request.user)
        appointment = Appointment.objects.select_related(
            'patient',
            'patient__user_profile',
            'doctor',
            'doctor__user_profile',
            'slot',
        ).get(pk=pk)
        if not can_access_appointment(profile, appointment):
            return Response({'detail': 'Not allowed.'}, status=403)
        return Response(AppointmentSerializer(appointment).data)


class AppointmentStatusView(APIView):
    def patch(self, request, pk):
        profile, error = require_role(request, UserProfile.ROLE_DOCTOR)
        if error:
            return error

        serializer = AppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = Appointment.objects.select_related('doctor').get(pk=pk)

        if appointment.doctor_id != profile.doctor_profile.id:
            return Response({'detail': 'Not allowed.'}, status=403)

        appointment.status = serializer.validated_data['status']
        appointment.save(update_fields=['status'])
        return Response(AppointmentSerializer(appointment).data)


class CallSignalView(APIView):
    def get(self, request, pk):
        profile = ensure_profile(request.user)
        appointment = Appointment.objects.select_related('doctor', 'patient').get(pk=pk)
        if not can_access_appointment(profile, appointment):
            return Response({'detail': 'Not allowed.'}, status=403)

        after = int(request.query_params.get('after', 0))
        signals = appointment.signals.filter(recipient_role=profile.role, id__gt=after)
        return Response(
            [
                {
                    'id': signal.id,
                    'kind': signal.kind,
                    'payload': signal.payload,
                    'created_at': signal.created_at,
                }
                for signal in signals
            ]
        )

    def post(self, request, pk):
        profile = ensure_profile(request.user)
        appointment = Appointment.objects.select_related('doctor', 'patient').get(pk=pk)
        if not can_access_appointment(profile, appointment):
            return Response({'detail': 'Not allowed.'}, status=403)

        serializer = CallSignalWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient_role = (
            UserProfile.ROLE_PATIENT if profile.role == UserProfile.ROLE_DOCTOR else UserProfile.ROLE_DOCTOR
        )
        signal = CallSignal.objects.create(
            appointment=appointment,
            sender=profile,
            recipient_role=recipient_role,
            kind=serializer.validated_data['kind'],
            payload=serializer.validated_data.get('payload', {}),
        )
        return Response({'id': signal.id}, status=201)
