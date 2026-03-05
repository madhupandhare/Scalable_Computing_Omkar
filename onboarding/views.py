from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Student
from .serializers import RegisterStudentSerializer, StudentSerializer
from .services import CountryInfoService, IDCardService, RestaurantService
from .aws_queue import WelcomePackQueueService


def home(request):
    return render(request, 'onboarding/register.html')


def dashboard(request):
    return render(request, 'onboarding/dashboard.html')


@api_view(['POST'])
def register_student(request):
    serializer = RegisterStudentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    payload = serializer.validated_data

    # Here we validate the student payload and then request a digital card id.
    id_response = IDCardService.generate_card(payload)

    student = Student.objects.create(**payload, card_id=id_response['card_id'])
    response_data = StudentSerializer(student).data
    response_data['id_service'] = id_response['raw_response']

    return Response(
        {
            'message': 'Student registered successfully.',
            'student': response_data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
def get_restaurants(request):
    student_id = request.data.get('student_id')
    cuisine = request.data.get('cuisine')
    budget = request.data.get('budget')

    if not all([student_id, cuisine, budget]):
        return Response(
            {'error': 'student_id, cuisine, and budget are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    student = get_object_or_404(Student, id=student_id)

    # This section connects to the external restaurant API.
    restaurants = RestaurantService.get_recommendations(student.campus_city, cuisine, budget)

    return Response(
        {
            'student_id': student.id,
            'campus_city': student.campus_city,
            'restaurants': restaurants,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
def country_info(request):
    country_name = request.GET.get('country')
    if not country_name:
        return Response({'error': 'country query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    data = CountryInfoService.fetch_country_info(country_name)
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def student_detail(request, student_id: int):
    student = get_object_or_404(Student, id=student_id)
    return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def trigger_welcome_pack(request):
    student_id = request.data.get('student_id')
    if not student_id:
        return Response({'error': 'student_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    student = get_object_or_404(Student, id=student_id)
    queue_result = WelcomePackQueueService.enqueue(
        student_id=student.id,
        campus_city=student.campus_city,
        home_country=student.home_country,
    )

    return Response(
        {
            'message': 'Welcome pack event sent.',
            'student_id': student.id,
            **queue_result,
        },
        status=status.HTTP_202_ACCEPTED,
    )
