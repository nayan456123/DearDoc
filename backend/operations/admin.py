from django.contrib import admin

from .models import Appointment, AvailabilitySlot, CallSignal, DoctorProfile, PatientProfile, UserProfile

admin.site.register(UserProfile)
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(AvailabilitySlot)
admin.site.register(Appointment)
admin.site.register(CallSignal)
