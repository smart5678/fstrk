from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import proxy_request
from .throttle import DuplicateError, DuplicateThrottle


class GatewayView(APIView):
    throttle_classes = [DuplicateThrottle]

    def post(self, request):
        task = proxy_request.apply_async([request.data, dict(request.headers)])
        headers = {'X-Celery-ID': str(task.id)} if settings.DEBUG else None
        return Response(status=status.HTTP_200_OK, headers=headers)

    def throttled(self, request, wait):
        """
        В любом случае возвращаем 200
        TODO: возвращать заголовок с id taska который дублируется?
        """
        raise DuplicateError


class DebugView(APIView):
    def post(self, request):
        return Response(status=status.HTTP_200_OK)
