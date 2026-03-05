import json
import logging
from typing import Any

import boto3
from django.conf import settings

logger = logging.getLogger(__name__)


class WelcomePackQueueService:
    @staticmethod
    def enqueue(student_id: int, campus_city: str, home_country: str) -> dict[str, Any]:
        if not settings.WELCOME_PACK_QUEUE_URL:
            # This fallback keeps local development simple when AWS is not configured yet.
            return {
                'queued': False,
                'message_id': None,
                'note': 'Queue URL is missing. Add WELCOME_PACK_QUEUE_URL in .env to enable SQS.',
            }

        message_payload = {
            'student_id': student_id,
            'campus_city': campus_city,
            'home_country': home_country,
            'event': 'generate_welcome_pack',
        }

        session_kwargs = {'region_name': settings.AWS_REGION}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs.update(
                {
                    'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                    'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
                }
            )

        sqs_client = boto3.client('sqs', **session_kwargs)

        try:
            response = sqs_client.send_message(
                QueueUrl=settings.WELCOME_PACK_QUEUE_URL,
                MessageBody=json.dumps(message_payload),
            )
            logger.info('Welcome pack event queued for student %s', student_id)
            return {
                'queued': True,
                'message_id': response.get('MessageId'),
                'note': 'Message pushed to SQS. Lambda consumer can now generate the welcome pack.',
            }
        except Exception as exc:
            logger.warning('Unable to queue welcome pack message: %s', exc)
            return {
                'queued': False,
                'message_id': None,
                'note': 'SQS send failed. Check AWS credentials, region, and queue URL.',
            }
