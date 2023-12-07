from rest_framework import serializers

from reports.models import translate_crop_status, CropStatus
from .models import UserDiagnosisRequest, CropCategory


class UserDiagnosisRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDiagnosisRequest
        fields = '__all__'


def serialize_ranking(possibility_ranking: list[float], disease_ranking: list[str]) -> tuple[
    list[dict[str, int | str]], CropCategory or str]:
    """
    Serialize the ranking data to JSON format.
    :param possibility_ranking: Possibility ranking data
    :param disease_ranking: Disease ranking data
    :return: Serialized ranking data
    """
    # Make a list of dictionaries
    # [
    #     {
    #         "rank": 1,
    #         "state": "HEALTHY",
    #         "probability": "80.2"
    #     },
    #     {
    #         "rank": 2,
    #         "state": "STRAWBERRY_LEAF_SCORCH",
    #         "probability": "19.8"
    #     }
    # ]
    ranking = []
    for i in range(len(possibility_ranking)):
        entity = {
            'rank': i + 1,
            'state': disease_ranking[i],
            'probability': str(possibility_ranking[i])
        }
        ranking.append(entity)

    translated_disease = translate_crop_status(disease_ranking[0])

    # Convert disease_ranking[0] to CropCategory
    return ranking, CropStatus[translated_disease]
