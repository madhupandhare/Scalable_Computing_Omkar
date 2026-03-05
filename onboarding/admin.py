from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'campus_city', 'course', 'card_id')
    search_fields = ('first_name', 'last_name', 'email', 'campus_city', 'home_country')
