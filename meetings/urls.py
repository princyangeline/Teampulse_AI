from django.urls import path
from . import views

urlpatterns = [
    path('', views.executive_dashboard, name='executive_dashboard'),
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('upload/', views.upload_transcript, name='upload_transcript'),
    path('meeting/<int:pk>/', views.meeting_dashboard, name='meeting_dashboard'),
    path('meeting/<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
    path('trends/', views.trends_dashboard, name='trends_dashboard'),
    path('health/', views.team_health_index, name='team_health_index'),
    path('comparison/', views.meeting_comparison, name='meeting_comparison'),
    path('risks/', views.risk_filter, name='risk_filter'),
    
    # Export endpoints
    path('meeting/<int:pk>/export/pdf/', views.export_meeting_pdf, name='export_meeting_pdf'),
    path('meeting/<int:pk>/export/excel/', views.export_meeting_excel, name='export_meeting_excel'),
    path('export/team-health/pdf/', views.export_team_health_pdf, name='export_team_health_pdf'),
    path('export/team-health/excel/', views.export_team_health_excel, name='export_team_health_excel'),
    
    # Email digest
    path('send-digest/', views.send_email_digest, name='send_email_digest'),
]
