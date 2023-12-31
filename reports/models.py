from django.core.exceptions import ValidationError
from django.db import models

import diagnosis.models
from accounts.models import User, RequestUser
import uuid
from diagnosis.models import CropCategory, UserDiagnosisRequest


class CropStatus(models.TextChoices):
    UNKNOWN = '알 수 없음'
    HEALTHY = '정상'
    ERROR = '오류'

    # Tomato states
    GRAY_MOLD = '잿빛곰팡이병'
    POWDERY_MILDEW = '흰가루병'
    DOWNY_MILDEW = '노균병'
    ANTHRACNOSE = '탄저병'

    MACRONUTRIENT_DEFICIENCY_NITROGEN = '다량원소결핍(N)'
    MACRONUTRIENT_DEFICIENCY_PHOSPHORUS = '다량원소결핍(P)'
    MACRONUTRIENT_DEFICIENCY_POTASSIUM = '다량원소결핍(K)'
    DEHISCENCE = '열과'
    COLD_INJURY = '냉해피해'
    CALCIUM_DEFICIENCY_ = '칼슘결핍'


def translate_crop_status(crop_status: str) -> str:

    match (crop_status):
        case '알 수 없음':
            return 'UNKNOWN'
        case '정상':
            return 'HEALTHY'
        case '오류':
            return 'ERROR'
        case '잿빛곰팡이병':
            return 'GRAY_MOLD'
        case '흰가루병':
            return 'POWDERY_MILDEW'
        case '노균병':
            return 'DOWNY_MILDEW'
        case '탄저병':
            return 'ANTHRACNOSE'
        case '다량원소결핍(N)':
            return 'MACRONUTRIENT_DEFICIENCY_NITROGEN'
        case '다량원소결핍(P)':
            return 'MACRONUTRIENT_DEFICIENCY_PHOSPHORUS'
        case '다량원소결핍(K)':
            return 'MACRONUTRIENT_DEFICIENCY_POTASSIUM'
        case '열과':
            return 'DEHISCENCE'
        case '냉해피해':
            return 'COLD_INJURY'
        case '칼슘결핍':
            return 'CALCIUM_DEFICIENCY_'


class UserDiagnosisResult(models.Model):

    id = models.UUIDField(primary_key=True,
                          editable=False)
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
                # if not isinstance(probability, float) or probability < 0.0 or probability > 100.0:
                #     raise ValidationError('Probability must be a float between 0.0 and 100.0')
                # probability_sum += probability
            # AI Server must match the sum of probabilities to 100.0 prior to processing in this server
            # if int(probability_sum) != 100:
            #     raise ValidationError('Sum of probabilities must be 100.0')

        except AttributeError:
            raise ValidationError('This ranking structure is invalid')

    class Meta:
        db_table = 'user_diagnosis_report'
        managed = True
