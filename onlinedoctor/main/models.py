from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings  # LANGUAGES ni import qilish uchun

# User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('patient', 'Patient'), ('doctor', 'Doctor')], default='patient')
    name = models.CharField(max_length=100, blank=True, default='')
    age = models.PositiveIntegerField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    theme = models.CharField(max_length=20, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    languages = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Patient
class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    registration_date = models.DateField(auto_now_add=True)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

# Medical Record
class MedicalRecord(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    test_results = models.TextField(blank=True, help_text="Save test results here")
    examination_notes = models.TextField(blank=True, help_text="Examination notes")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.name}'s Record"

# Doctor
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    patients = models.ManyToManyField(Patient, related_name='doctors')
    reviews = models.TextField(blank=True, help_text="Doctor's reviews about patients")
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    experience_years = models.IntegerField(default=0, blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# Appointment
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient.name} with {self.doctor.name} on {self.date}"

# Clinic
class Clinic(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    reviews = models.TextField(blank=True, help_text="Clinic reviews")

    def __str__(self):
        return self.name

# Review
class Review(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name}'s review for {self.doctor.name}"