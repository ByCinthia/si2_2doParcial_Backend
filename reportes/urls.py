from django.urls import path
from .views import DynamicReportView, VoiceReportView, ReportStatusView

urlpatterns = [
    path('dynamic_report/', DynamicReportView.as_view(), name='dynamic-report'),
    path('voice_report/', VoiceReportView.as_view(), name='voice-report'),
    path('status/', ReportStatusView.as_view(), name='report-status'),
]