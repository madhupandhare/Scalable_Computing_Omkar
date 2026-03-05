from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/register-student', views.register_student, name='register-student'),
    path('api/get-restaurants', views.get_restaurants, name='get-restaurants'),
    path('api/country-info', views.country_info, name='country-info'),
    path('api/student/<int:student_id>', views.student_detail, name='student-detail'),
    path('api/generate-welcome-pack', views.trigger_welcome_pack, name='generate-welcome-pack'),
]
