from django.core.exceptions import ValidationError
from django.db import models

import diagnosis.models
from accounts.models import User, RequestUser
import uuid
from diagnosis.models import CropCategory, UserDiagnosisRequest


class CropStatus(models.TextChoices):
    UNKNOWN = 'UNKNOWN'
    HEALTHY = 'HEALTHY'
    ERROR = 'ERROR'

    # Tomato states
    TOMATO_GRAY_MOLD = 'TOMATO_GRAY_MOLD'
    TOMATO_POWDERY_MILDEW = 'TOMATO_POWDERY_MILDEW'
    TOMATO_MACRONUTRIENT_DEFICIENCY = 'TOMATO_MACRONUTRIENT_DEFICIENCY'
    TOMATO_DEHISCENCE = 'TOMATO_DEHISCENCE'

    # Strawberry states
    STRAWBERRY_GRAY_MOLD = 'STRAWBERRY_GRAY_MOLD'
    STRAWBERRY_POWDERY_MILDEW = 'STRAWBERRY_POWDERY_MILDEW'
    STRAWBERRY_MACRONUTRIENT_DEFICIENCY = 'STRAWBERRY_MACRONUTRIENT_DEFICIENCY'
    STRAWBERRY_COLD_INJURY = 'STRAWBERRY_COLD_INJURY'

    # Cucumber states
    CUCUMBER_DOWNY_MILDEW = 'CUCUMBER_DOWNY_MILDEW'
    CUCUMBER_POWDERY_MILDEW = 'CUCUMBER_POWDERY_MILDEW'
    CUCUMBER_MACRONUTRIENT_DEFICIENCY = 'CUCUMBER_MACRONUTRIENT_DEFICIENCY'
    CUCUMBER_COLD_INJURY = 'CUCUMBER_COLD_INJURY'

    # Pepper states
    PEPPER_ANTHRACNOSE = 'PEPPER_ANTHRACNOSE'
    PEPPER_POWDERY_MILDEW = 'PEPPER_POWDERY_MILDEW'
    PEPPER_MACRONUTRIENT_DEFICIENCY = 'PEPPER_MACRONUTRIENT_DEFICIENCY'


class UserDiagnosisResult(models.Model):

    id = models.UUIDField(primary_key=True,
                          editable=False,
                          default=uuid.uuid4().hex)
    request_user_id = models.ForeignKey(RequestUser,
                                        on_delete=models.SET_NULL,
                                        null=True)
    request_id = models.ForeignKey(UserDiagnosisRequest,
                                   on_delete=models.SET_NULL,
                                   null=True)
    created_date = models.DateTimeField(auto_now_add=True,
                                        editable=False)
    crop_category = models.CharField(max_length=50,
                                     blank=False,
                                     choices=CropCategory.choices)
    crop_status = models.CharField(max_length=50,
                                   blank=True,
                                   choices=CropStatus.choices)
    probability_ranking = models.JSONField(
        blank=False,
        null=False,
    )
    # NOT_YET_IMPLEMENTED
    # crop_status_data
    '''
    "rank_counts": 2,
    "crop_status_possibility_rank": [
        {
            "rank": 1
            "status": "HEALTHY",
            "probability": "80.2"
        },
        {
            "rank": 2,
            "state": "STRAWBERRY_LEAF_SCORCH",
            "probability": "19.8"
        }
    ]
    '''


    def clean(self):
        super().clean()
        try:
            rank_counts = self.probability_ranking.get('rank_counts', 0)
            if not isinstance(rank_counts, int) or rank_counts == 0:
                raise ValidationError('Rank_counts must be a positive integer')

            ranking = self.probability_ranking.get('ranking', None)
            if ranking is None or len(ranking) == 0:
                raise ValidationError('Ranking must not be empty')
            probability_sum = 0.0

            for entity in ranking:
                if not isinstance(entity, dict):
                    raise ValidationError('Ranking structure is invalid')

                rank = entity.get('rank', None)
                state = entity.get('state', None)
                probability = entity.get('probability', None)
                if not isinstance(rank, int) or rank < 0:
                    raise ValidationError('Rank must be a positive integer')
                if not isinstance(state, str):
                    raise ValidationError('State must be a string')
                elif state not in CropStatus.values:
                    raise ValidationError('Invalid state value')
                if not isinstance(probability, float) or probability < 0.0 or probability > 100.0:
                    raise ValidationError('Probability must be a float between 0.0 and 100.0')
                probability_sum += probability
            # AI Server must match the sum of probabilities to 100.0 prior to processing in this server
            if int(probability_sum) != 100:
                raise ValidationError('Sum of probabilities must be 100.0')

        except AttributeError:
            raise ValidationError('This ranking structure is invalid')

    class Meta:
        db_table = 'user_diagnosis_report'
        managed = True
