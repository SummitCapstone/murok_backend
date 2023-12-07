# This file contains task codes which are ran in RabbitMQ.
import traceback
import uuid

import dramatiq
import requests
from django.db import IntegrityError

from accounts.models import RequestUser
from .models import UserDiagnosisRequest, CropCategory
from .serializers import serialize_ranking
from .exceptions import AIServerError
from murok_backend.settings import BASE_DIR, AI_SERVER_URL
from reports.models import UserDiagnosisResult
import django.db.transaction

import logging


@dramatiq.actor(queue_name='aiserver_request',
                actor_name='send_diagnosis_data_to_aiserver',
                priority=1)
def send_diagnosis_data_to_aiserver(request_data: dict,
                                    crop_category: CropCategory) -> dict:
    try:
        '''
        Required data
        
        picture_path: str
        id: uuid str
        request_user_id: uuid str
        
        '''
        picture_path = request_data.get('picture_path')
        request_id = request_data.get('id')
        request_user_id = request_data.get('request_user_id')

        # Get an absolute path of the image file

        file_path = BASE_DIR / picture_path
        logging.debug('Uploaded file path: %s', file_path)

        # Decapitalize letter
        crop_category = crop_category.lower()
        str_data = {'crop_type': crop_category}
        # Send the image file to the AI server
        with open(file_path, 'rb') as f:
            image_file = {'image': (str(file_path), f)}
            logging.info('Sending request %s sent by %s to AI server %s',
                         request_id, request_user_id,
                         AI_SERVER_URL)
            diagnosis_result = requests.post(AI_SERVER_URL, files=image_file, data=str_data)

        logging.info('Diagnosis result of request %s sent by %s : %s',
                     request_id,
                     request_user_id,
                     diagnosis_result.status_code)
        print(diagnosis_result.status_code)
        print(diagnosis_result)
    except Exception:
        # Print stack trace
        traceback.print_exc()
        logging.debug('Traceback: %s', traceback.format_exc())

        # Halt the job and raise AIServerError
        raise AIServerError('AI Server Error')
    else:
        # Serialize the response object to JSON
        return {
            'id': request_id,
            'request_user_id': request_user_id,
            'crop_category': crop_category,
            'response': diagnosis_result.json()
        }
    # Send the image to AI server.


@dramatiq.actor(queue_name='aiserver_request',
                priority=1)
@django.db.transaction.atomic
def validate_and_save_to_db(data: dict) -> str or uuid.UUID:
    '''
    Required data

    id: uuid str
    request_user_id: uuid str

    '''
    request_id = data.get('id')
    request_user_id = data.get('request_user_id')
    crop_category = data.get('crop_category')
    response = data.get('response')

    try:
        disease_ranking = response['top_diseases']
        disease_possibility_ranking = response['top_probabilities']

        # Serialize the ranking data
        ranking, crop_stat = serialize_ranking(disease_possibility_ranking, disease_ranking)
        logging.debug('Serialized ranking data: %s', ranking)
        logging.info('Most probable crop status of request %s sent by %s : %s',
                     crop_stat,
                     request_id, request_user_id)

        # Make a new entity of UserDiagnosisResult
        result = UserDiagnosisResult.objects.create(
            id=uuid.uuid4().hex,
            request_user_id=RequestUser.objects.get(id=request_user_id),
            request_id=UserDiagnosisRequest.objects.get(id=request_id),
            crop_category=crop_category,
            crop_status=crop_stat,
            probability_ranking=ranking
        )
        logging.info('Created a new UserDiagnosisResult with id: %s sent by %s',
                     result.id,
                     result.request_user_id.id)
    except IntegrityError:
        logging.critical('IntegrityError occurred while saving UserDiagnosisResult to database.')
        logging.critical('Failed response\'s request_id: %s sent by RequestUser %s',
                         request_id,
                         request_user_id)
        logging.debug('Traceback: %s', traceback.format_exc())
    else:
        return result.id


# Send a notification to user when the diagnosis is done. With Web Push API!
def send_web_push(report_id: uuid.UUID or str) -> None:
    pass

