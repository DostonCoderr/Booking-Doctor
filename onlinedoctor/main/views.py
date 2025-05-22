from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Patient, MedicalRecord, Doctor, Appointment, Clinic, UserProfile, Review
from .forms import AppointmentForm, MedicalRecordForm, UserProfileForm, ReviewForm
from django.utils.translation import activate, get_language
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

def home(request):
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile
        except ObjectDoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)
        patient = Patient.objects.get_or_create(email=request.user.email, defaults={'name': request.user.username})[0]
        appointments = Appointment.objects.filter(patient=patient).values('id', 'doctor__name', 'date', 'status')
        return render(request, 'authenticated_home.html', {'user_profile': user_profile, 'appointments': list(appointments)})
    return render(request, 'index.html')

@login_required
def booking(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            patient, created = Patient.objects.get_or_create(email=request.user.email, defaults={'name': request.user.username})
            appointment.patient = patient
            appointment.save()
            messages.success(request, 'Uchrashuv muvaffaqiyatli band qilindi!')
            return redirect('booking_track')
    else:
        form = AppointmentForm()
    return render(request, 'booking.html', {'form': form, 'user_profile': user_profile})

@login_required
def booking_track(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    patient = Patient.objects.get_or_create(email=request.user.email, defaults={'name': request.user.username})[0]
    appointments = Appointment.objects.filter(patient=patient).order_by('date')
    return render(request, 'booking_track.html', {'user_profile': user_profile, 'appointments': appointments})

@login_required
def doctors(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    doctors = Doctor.objects.all()
    return render(request, 'doctors.html', {'doctors': doctors, 'user_profile': user_profile})

@login_required
def doctor_detail(request, doctor_id):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor)
    return render(request, 'doctor_detail.html', {'doctor': doctor, 'reviews': reviews, 'user_profile': user_profile})

@login_required
def records(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    patient, created = Patient.objects.get_or_create(email=request.user.email, defaults={'name': request.user.username})
    records = MedicalRecord.objects.filter(patient=patient)
    if request.method == 'POST':
        record_form = MedicalRecordForm(request.POST)
        if record_form.is_valid():
            record = record_form.save(commit=False)
            record.patient = patient
            record.save()
            return redirect('records')
    else:
        record_form = MedicalRecordForm()
    doctor_reviews = Doctor.objects.filter(patients=patient).values_list('reviews', flat=True)
    clinic_reviews = Clinic.objects.all().values_list('reviews', flat=True)
    return render(request, 'records.html', {
        'records': records,
        'record_form': record_form,
        'doctor_reviews': doctor_reviews,
        'clinic_reviews': clinic_reviews,
        'user_profile': user_profile,
    })

@login_required
def update_record(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    patient, created = Patient.objects.get_or_create(email=request.user.email, defaults={'name': request.user.username})
    try:
        record = MedicalRecord.objects.get(patient=patient)
    except MedicalRecord.DoesNotExist:
        record = None

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            new_record = form.save(commit=False)
            new_record.patient = patient
            new_record.save()
            return redirect('records')
    else:
        form = MedicalRecordForm(instance=record)
    return render(request, 'records.html', {'record_form': form, 'records': MedicalRecord.objects.filter(patient=patient), 'user_profile': user_profile})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            patient, created = Patient.objects.get_or_create(email=email, defaults={'name': username})
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    return render(request, 'registration/register.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def doctor_review(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    patient = Patient.objects.get_or_create(email=request.user.email, defaults={'name': request.user.username})[0]
    latest_appointment = Appointment.objects.filter(patient=patient, status='completed').order_by('-end_time').first()
    if request.method == 'POST' and latest_appointment:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.patient = patient
            review.doctor = latest_appointment.doctor
            review.save()
            messages.success(request, 'Review muvaffaqiyatli saqlandi!')
            return redirect('booking_track')
    else:
        form = ReviewForm()
    return render(request, 'doctor_review.html', {'form': form, 'user_profile': user_profile, 'appointment': latest_appointment})

@login_required
def profile(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST' and 'edit_profile' in request.POST:
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'profile.html', {'form': form, 'user_profile': user_profile})

@login_required
def settings(request):
    try:
        user_profile = request.user.userprofile
    except ObjectDoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST' and 'save_settings' in request.POST:
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('settings')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'settings.html', {'form': form, 'user_profile': user_profile})

@login_required
def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language', 'en')
        request.session['django_language'] = language
        activate(language)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def admin_accept_appointment(request, appointment_id):
    if request.user.is_staff:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.status == 'pending':
            appointment.status = 'accepted'
            appointment.save()
            messages.success(request, 'Uchrashuv qabul qilindi!')
        return redirect('admin:index')
    return redirect('home')

@login_required
def admin_start_appointment(request, appointment_id):
    if request.user.is_staff:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.status == 'accepted':
            appointment.status = 'in_progress'
            appointment.start_time = timezone.now()
            appointment.save()
            messages.success(request, 'Uchrashuv boshlandi!')
        return redirect('admin:index')
    return redirect('home')

@login_required
def admin_end_appointment(request, appointment_id):
    if request.user.is_staff:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.status == 'in_progress':
            appointment.status = 'completed'
            appointment.end_time = timezone.now()
            appointment.save()
            messages.success(request, 'Uchrashuv tugadi!')
            patient = appointment.patient
            return redirect('doctor_review')  # Review sahifasiga yo'naltirish
        return redirect('admin:index')
    return redirect('home')

@login_required
def admin_completion_form(request, appointment_id):
    if request.user.is_staff:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if request.method == 'POST':
            comment = request.POST.get('comment', 'Ish hal bo‘ldi')
            appointment.notes += f"\nShifokor izohi: {comment}"
            appointment.save()
            messages.success(request, 'Izoh saqlandi!')
            return redirect('admin:index')
        return render(request, 'admin_completion_form.html', {'appointment': appointment})
    return redirect('home')