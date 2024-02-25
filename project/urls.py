from django.urls import path

from gateway.views import DebugView, GatewayView

urlpatterns = [
    path('', GatewayView.as_view(), name='gateway'),
    path('debug', DebugView.as_view()),
]
