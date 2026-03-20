from rest_framework import status
from rest_framework.exceptions import APIException

class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "동일한 데이터가 이미 존재합니다."