from __future__ import annotations

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class IDCardService:
    @staticmethod
    def generate_card(student_payload: dict[str, Any]) -> dict[str, Any]:
        headers = {'Content-Type': 'application/json'}
        if settings.ID_CARD_API_KEY:
            headers['Authorization'] = f'Bearer {settings.ID_CARD_API_KEY}'

        try:
            response = requests.post(settings.ID_CARD_API_URL, json=student_payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'card_id': data.get('cardId') or data.get('id') or 'pending-card-id',
                'raw_response': data,
            }
        except requests.RequestException as exc:
            logger.warning('ID card service request failed: %s', exc)
            # We return a fallback card id so registration is still usable in offline demos.
            fallback = f"local-{student_payload.get('email', 'student').replace('@', '-at-')}"
            return {'card_id': fallback, 'raw_response': {'warning': 'fallback_card_used'}}


class RestaurantService:
    @staticmethod
    def get_recommendations(campus_city: str, cuisine: str, budget: str) -> list[dict[str, Any]]:
        headers = {'Content-Type': 'application/json'}
        if settings.RESTAURANT_API_KEY:
            headers['Authorization'] = f'Bearer {settings.RESTAURANT_API_KEY}'

        payload = {
            'city': campus_city,
            'cuisine': cuisine,
            'budget': budget,
        }

        try:
            response = requests.post(settings.RESTAURANT_API_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and 'restaurants' in data:
                return data['restaurants']
            if isinstance(data, list):
                return data
            return []
        except requests.RequestException as exc:
            logger.warning('Restaurant service request failed: %s', exc)
            # We provide practical fallback recommendations for classroom testing.
            return [
                {
                    'name': f'{cuisine.title()} Hub',
                    'city': campus_city,
                    'budget': budget,
                    'rating': 4.2,
                    'note': 'Fallback suggestion because external API is unavailable.',
                }
            ]


class CountryInfoService:
    @staticmethod
    def fetch_country_info(country_name: str) -> dict[str, Any]:
        try:
            response = requests.get(f"{settings.COUNTRY_API_URL}/{country_name}", timeout=10)
            response.raise_for_status()
            payload = response.json()[0]

            currencies = payload.get('currencies', {})
            currency_key = next(iter(currencies.keys()), '')
            currency_data = currencies.get(currency_key, {})

            return {
                'country': payload.get('name', {}).get('common', country_name),
                'currency': currency_key,
                'currency_name': currency_data.get('name', ''),
                'currency_symbol': currency_data.get('symbol', ''),
                'timezone': payload.get('timezones', [''])[0],
                'calling_code': f"+{payload.get('idd', {}).get('root', '').replace('+', '')}{payload.get('idd', {}).get('suffixes', [''])[0]}",
                'flag': payload.get('flags', {}).get('png', ''),
                'region': payload.get('region', ''),
            }
        except (requests.RequestException, IndexError, KeyError, TypeError) as exc:
            logger.warning('Country info request failed: %s', exc)
            return {
                'country': country_name,
                'currency': 'N/A',
                'currency_name': 'Not available',
                'currency_symbol': '',
                'timezone': 'Not available',
                'calling_code': 'Not available',
                'flag': '',
                'region': 'Not available',
            }
