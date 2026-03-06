from django.contrib import admin

from .models import Appointment, CareTask, Clinic, Clinician, IntakeRequest, OperationalSignal, Patient, UserProfile

admin.site.register(UserProfile)
admin.site.register(Clinic)
admin.site.register(Clinician)
admin.site.register(Patient)
admin.site.register(IntakeRequest)
admin.site.register(Appointment)
admin.site.register(CareTask)
admin.site.register(OperationalSignal)
