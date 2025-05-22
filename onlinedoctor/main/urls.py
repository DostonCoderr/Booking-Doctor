from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('booking-track/', views.booking_track, name='booking_track'),  # 'booking-success' o'rniga 'booking-track'
    path('doctors/', views.doctors, name='doctors'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('records/', views.records, name='records'),
    path('update-record/', views.update_record, name='update_record'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('doctor-review/', views.doctor_review, name='doctor_review'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('admin/accept-appointment/<int:appointment_id>/', views.admin_accept_appointment, name='admin_accept_appointment'),
    path('admin/start-appointment/<int:appointment_id>/', views.admin_start_appointment, name='admin_start_appointment'),
    path('admin/end-appointment/<int:appointment_id>/', views.admin_end_appointment, name='admin_end_appointment'),
    path('admin/completion-form/<int:appointment_id>/', views.admin_completion_form, name='admin_completion_form'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


