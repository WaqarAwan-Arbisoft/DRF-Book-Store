"""
Custom Exception Module
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler
    """
    response = exception_handler(exc, context)
    if (response is not None):
        return response
    exceptionMsg = str(exc).strip('()').split(',')
    return Response({'detail': exceptionMsg[0].strip("''")},
                    status=int(exceptionMsg[1])
                    )
