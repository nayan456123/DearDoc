import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=120)),
                ('role', models.CharField(choices=[('doctor', 'Doctor'), ('patient', 'Patient')], default='patient', max_length=20)),
                ('headline', models.CharField(blank=True, max_length=140)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialty', models.CharField(max_length=120)),
                ('bio', models.TextField()),
                ('years_experience', models.PositiveIntegerField(default=0)),
                ('room_label', models.CharField(max_length=80)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profile', to='operations.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.PositiveIntegerField(default=18)),
                ('location', models.CharField(max_length=120)),
                ('primary_goal', models.CharField(max_length=160)),
                ('emergency_contact', models.CharField(blank=True, max_length=80)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient_profile', to='operations.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='AvailabilitySlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('booked', 'Booked'), ('blocked', 'Blocked')], default='open', max_length=20)),
                ('visit_mode', models.CharField(choices=[('video', 'Video'), ('audio', 'Audio')], default='video', max_length=20)),
                ('label', models.CharField(blank=True, max_length=80)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_slots', to='operations.doctorprofile')),
            ],
            options={
                'ordering': ['starts_at'],
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('confirmed', 'Confirmed'), ('live', 'Live'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='requested', max_length=20)),
                ('concern', models.CharField(max_length=180)),
                ('symptoms', models.TextField()),
                ('patient_notes', models.TextField(blank=True)),
                ('urgency', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='low', max_length=20)),
                ('triage_score', models.PositiveIntegerField(default=0)),
                ('copilot_summary', models.TextField()),
                ('copilot_checklist', models.JSONField(blank=True, default=list)),
                ('innovation_tag', models.CharField(default='PulseMatch Copilot', max_length=120)),
                ('meeting_code', models.CharField(max_length=32, unique=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='operations.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='operations.patientprofile')),
                ('slot', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment', to='operations.availabilityslot')),
            ],
            options={
                'ordering': ['starts_at'],
            },
        ),
        migrations.CreateModel(
            name='CallSignal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient_role', models.CharField(choices=[('doctor', 'Doctor'), ('patient', 'Patient')], max_length=20)),
                ('kind', models.CharField(choices=[('offer', 'Offer'), ('answer', 'Answer'), ('candidate', 'Candidate'), ('ready', 'Ready'), ('end', 'End')], max_length=20)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signals', to='operations.appointment')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_signals', to='operations.userprofile')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
