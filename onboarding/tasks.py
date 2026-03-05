from .models import Student
from .services import CountryInfoService, RestaurantService


def build_welcome_pack(student_id: int) -> dict:
    student = Student.objects.get(id=student_id)
    profile = {
        'full_name': f'{student.first_name} {student.last_name}',
        'email': student.email,
        'course': student.course,
        'campus_city': student.campus_city,
        'card_id': student.card_id,
    }
    country_info = CountryInfoService.fetch_country_info(student.home_country)
    restaurants = RestaurantService.get_recommendations(student.campus_city, cuisine='local', budget='medium')

    return {
        'student': profile,
        'country_info': country_info,
        'restaurant_suggestions': restaurants,
    }
