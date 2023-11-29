import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.http import JsonResponse

api_url = "http://ncpms.rda.go.kr/npmsAPI/service"
api_key = settings.API_KEY

def parse_xml_data(xml_data):
    # XML 문자열을 파싱
    root = ET.fromstring(xml_data)

    # 필요한 정보 추출
    crop_name = root.find(".//cropName").text
    sick_name_kor = root.find(".//sickNameKor").text
    sick_name_eng = root.find(".//sickNameEng").text
    development_condition = root.find(".//developmentCondition").text
    prevention_method = root.find(".//preventionMethod").text
    symptoms = root.find(".//symptoms").text
    infection_route = root.find(".//infectionRoute").text

    # 필요한 정보를 반환하거나 활용
    result = {
        'cropName': crop_name,
        'sickNameKor': sick_name_kor,
        'sickNameEng': sick_name_eng,
        'developmentCondition': development_condition,
        'preventionMethod': prevention_method,
        'symptoms': symptoms,
        'infectionRoute': infection_route,
    }

    return result

def call_api(request):
    # 첫 번째 API 호출
    crop_name = request.GET.get('cropName', '')
    sick_name_kor = request.GET.get('sickNameKor', '')
    request_param_sick = {
        'apiKey': api_key,
        'serviceCode': 'SVC01',  # 병 정보
        'serviceType': 'AA003',  # json type 반환
        'cropName': crop_name,
        'sickNameKor': sick_name_kor
    }

    try:
        response_sick = requests.get(api_url, params=request_param_sick)
        if response_sick.status_code == 200:
            api_data_sick = response_sick.json()
            print(f"first api response: {api_data_sick}")
            # sickKey 추출
            sick_key = api_data_sick['service']['list'][0]['sickKey']
            # 병피해 대표 이미지(썸네일)
            thumbImg = api_data_sick['service']['list'][0]['thumbImg']
            # 병피해 대표 이미지
            oriImg = api_data_sick['service']['list'][0]['oriImg']

            # 두 번째 API 호출
            request_param_sick_detail = {
                'apiKey': api_key,
                'serviceCode': 'SVC05',  # 병 상세 정보
                'sickKey': sick_key,
            }
            print("before second api")
            response_sick_detail = requests.get(api_url, params=request_param_sick_detail)

            if response_sick_detail.status_code == 200:
                # 여기서 파싱
                api_data_sick_detail = parse_xml_data(response_sick_detail.content)
                print(api_data_sick_detail)
                # 이미지 정보 추가
                api_data_sick_detail['thumbImg'] = thumbImg
                api_data_sick_detail['oriImg'] = oriImg
                return JsonResponse(api_data_sick_detail, status=200)
            else:
                return JsonResponse({'error': f"Error in second API call: {response_sick_detail.status_code}"}, status=response_sick_detail.status_code)

        else:
            return JsonResponse({'error': f"Error in first API call: {response_sick.status_code}"}, status=response_sick.status_code)

    except Exception as e:
        return JsonResponse({'error': f"Exception: {e}"}, status=400)
