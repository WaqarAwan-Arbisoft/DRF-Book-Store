"""
Custom Exception Module
"""
from http import HTTPStatus

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler
    """
    response = exception_handler(exc, context)
    if response is not None:
        http_code_to_message = {v.value: v.description for v in HTTPStatus}

        error_payload = {
            "error": {
                "status_code": 0,
                "message": "",
                "detail": "",
            }
        }
        respData = response.data[list(response.data.keys())[0]] if isinstance(
            response.data, dict) else response.data[0]
        error = error_payload["error"]
        status_code = response.status_code
        error["status_code"] = status_code
        error["message"] = http_code_to_message[status_code]
        error["detail"] = respData[0] if isinstance(
            respData, list) else respData
        response.data = error_payload
    return response
