from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'home_country',
            'campus_city',
            'course',
            'card_id',
            'created_at',
        ]

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class RegisterStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'home_country',
            'campus_city',
            'course',
        ]
