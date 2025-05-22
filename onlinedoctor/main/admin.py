from django.contrib import admin
from .models import Patient, MedicalRecord, Doctor, Appointment, Review

# Inline klasslar
class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    can_delete = False

class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 1

# Patient modelini admin panelda ko‘rsatish
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'registration_date')
    search_fields = ('name', 'email')
    list_filter = ('registration_date',)
    inlines = [MedicalRecordInline, AppointmentInline]

# MedicalRecord modelini admin panelda ko‘rsatish
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'diagnosis', 'last_updated')
    search_fields = ('patient__name', 'diagnosis')
    list_filter = ('last_updated',)

# Doctor modelini admin panelda ko‘rsatish
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'get_patient_count', 'image')
    search_fields = ('name', 'specialty')
    list_filter = ('specialty',)
    fields = ('name', 'specialty', 'image', 'experience_years', 'contact_info', 'patients', 'reviews')

    def get_patient_count(self, obj):
        return obj.patients.count()
    get_patient_count.short_description = 'Patient Count'

# Appointment modelini admin panelda ko‘rsatish
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'status', 'start_time', 'end_time')
    search_fields = ('patient__name', 'doctor__name', 'notes')
    list_filter = ('date', 'doctor', 'status')
    date_hierarchy = 'date'
    actions = ['accept_appointment', 'start_appointment', 'end_appointment']

    def accept_appointment(self, request, queryset):
        queryset.update(status='accepted')
    accept_appointment.short_description = "Qabul qilish"

    def start_appointment(self, request, queryset):
        from django.utils import timezone
        for appointment in queryset:
            if appointment.status == 'accepted':
                appointment.start_time = timezone.now()
                appointment.status = 'in_progress'
                appointment.save()
    start_appointment.short_description = "Boshlash"

    def end_appointment(self, request, queryset):
        from django.utils import timezone
        for appointment in queryset:
            if appointment.status == 'in_progress':
                appointment.end_time = timezone.now()
                appointment.status = 'completed'
                appointment.save()
    end_appointment.short_description = "Tugatish"

# Review modelini admin panelda ko‘rsatish
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'rating', 'created_at')
    search_fields = ('patient__name', 'doctor__name', 'comment')
    list_filter = ('rating', 'created_at')