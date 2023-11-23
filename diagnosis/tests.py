from django.test import TestCase
from rest_framework.test import APITestCase, RequestsClient, APIRequestFactory, APIClient
import pytest
import pytest_django
from accounts.models import User, RequestUser
from uuid import uuid4, UUID
from PIL import Image
import numpy as np

from diagnosis.models import UserDiagnosisRequest
from diagnosis.views import UserRequestDiagnosis


# Create your tests here.

# Make a diagnosis request

def create_random_image(width: int = 500, height: int = 500) -> Image:
    """
    Create a random image for test.
    :param width: Width of the image
    :param height: Height of the image
    :return: Image object
    """
    rand_array = np.random.randint(0, 256, (width, height, 3), dtype=np.uint8)
    return Image.fromarray(rand_array)


class GuestRequestTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.request_user = RequestUser.objects.create(
            id=uuid4())
        self.request_id = uuid4()
        self.crop_image = create_random_image()
        self.crop_category = 'STRAWBERRY'
        self.view = UserRequestDiagnosis.as_view()

    def test_guest_request_diagnosis(self):
        """
        Test whether the guest user can request diagnosis or not.
        :return:
        """
        # Create a request
        guest_diagnosis_request = self.factory.post('/diagnosis/request',
                                    {
                                        'crop_category': self.crop_category,
                                        'picture': self.crop_image,
                                    },
                                    format='multipart',
                                    headers={
                                        'X-Request-User-Id': str(self.request_user.id),
                                        'X-Request-Id': str(self.request_id)})

        guest_diagnosis_response = self.view(guest_diagnosis_request)

        # Check whether the response is 200 OK or not.
        self.assertEqual(guest_diagnosis_response.status_code, 200)

        # Check whether the request is created or not.
        self.assertTrue(UserDiagnosisRequest.objects.filter(request_uuid=self.request_id).exists())

        # Check whether the request is created with correct data or not.
        self.assertEqual(UserDiagnosisRequest.objects.get(id=self.request_id).id, self.request_id)
        self.assertEqual(UserDiagnosisRequest.objects.get(id=self.request_id).crop_image, self.crop_image)
        self.assertEqual(UserDiagnosisRequest.objects.get(id=self.request_id).request_user_id,
                         self.request_user)
