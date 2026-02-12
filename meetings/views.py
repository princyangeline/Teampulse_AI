from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from typing import List, Dict
from datetime import datetime

from .models import Meeting, Speaker, Message, MeetingMetrics
from .forms import TranscriptUploadForm
from .parsers import TranscriptParser, TranscriptValidator
from .analyzers import MessageAnalyzer, MeetingAnalyzer
from .trend_analyzer import TrendAnalyzer, SpeakerTrendAnalyzer
from .risk_detector import RiskDetector
from .insights_generator import TeamInsightsGenerator
from .utils import calculate_team_health_index  
from .email_digest import EmailDigestGenerator
from .report_generator import MeetingReportGenerator, TeamHealthReportGenerator
from .excel_exporter import MeetingExcelExporter, TeamHealthExcelExporter


def upload_transcript(request):
    """Handle transcript upload and processing"""
    if request.method == 'POST':
        form = TranscriptUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Extract form data
            title = form.cleaned_data['title']
            date = form.cleaned_data['date']
            duration_minutes = form.cleaned_data.get('duration_minutes')
            transcript_text = form.cleaned_data['transcript_text']
            
            # Validate transcript
            validator = TranscriptValidator()
            if not validator.validate(transcript_text):
                for error in validator.errors:
                    messages.error(request, error)
                return render(request, 'meetings/upload.html', {'form': form})
            
            # Parse transcript
            parser = TranscriptParser(transcript_text)
            parsed_data = parser.parse()
            
            if not parsed_data:
                messages.error(request, 'Failed to parse transcript. Please check the format.')
                return render(request, 'meetings/upload.html', {'form': form})
            
            try:
                with transaction.atomic():
                    # Create meeting
                    meeting = Meeting.objects.create(
                        title=title,
                        date=date,
                        duration_minutes=duration_minutes
                    )
                    
                    # Analyze and save
                    analyzer = MeetingAnalyzer(meeting, parsed_data)
                    analyzer.analyze_and_save()
                    
                    messages.success(request, f'Successfully analyzed meeting: {title}')
                    return redirect('meeting_dashboard', pk=meeting.pk)
                    
            except Exception as e:
                messages.error(request, f'Error processing meeting: {str(e)}')
                return render(request, 'meetings/upload.html', {'form': form})
    else:
        form = TranscriptUploadForm()
    
    return render(request, 'meetings/upload.html', {'form': form})


def meeting_dashboard(request, pk):
    """Display analytics dashboard for a meeting"""
    
    meeting = get_object_or_404(Meeting, pk=pk)
    metrics = meeting.metrics.select_related('speaker').all()
    
    # Prepare chart data
    participation_data = {
        'labels': [m.speaker.name for m in metrics],
        'data': [m.participation_percentage for m in metrics]
    }
    
    engagement_data = {
        'labels': [m.speaker.name for m in metrics],
        'data': [m.engagement_score for m in metrics]
    }
    
    sentiment_data = {
        'labels': [m.speaker.name for m in metrics],
        'data': [m.avg_sentiment for m in metrics]
    }
    
    context = {
        'meeting': meeting,
        'metrics': metrics,
        'participation_data': participation_data,
        'engagement_data': engagement_data,
        'sentiment_data': sentiment_data,
    }
    
    return render(request, 'meetings/dashboard.html', context)


def meeting_list(request):
    """List all meetings"""
    meetings = Meeting.objects.all().order_by('-date')
    return render(request, 'meetings/list.html', {'meetings': meetings})


def trends_dashboard(request):
    """Display trend analysis across all meetings"""
    
    meetings = Meeting.objects.all().order_by('date')
    
    if meetings.count() < 2:
        messages.info(request, 'Need at least 2 meetings for trend analysis')
        return redirect('meeting_list')
    
    # Analyze trends
    trend_analyzer = TrendAnalyzer(list(meetings))
    trends = trend_analyzer.get_comprehensive_analysis()
    
    # Analyze risks
    risk_detector = RiskDetector(list(meetings))
    risks = risk_detector.get_comprehensive_risk_analysis()
    
    context = {
        'meetings': meetings,
        'trends': trends,
        'risks': risks,
    }
    
    return render(request, 'meetings/trends.html', context)


def team_health_index(request):
    """Display overall team health score and metrics"""
    
    meetings = Meeting.objects.all().order_by('date')
    
    if meetings.count() < 3:
        messages.info(request, 'Need at least 3 meetings for team health analysis')
        return redirect('meeting_list')
    
    # Get recent meetings (last 5)
    recent_meetings = list(meetings[:5])
    
    # Calculate Team Health Index
    health_index = calculate_team_health_index(recent_meetings)
    
    # Get comprehensive risk analysis
    risk_detector = RiskDetector(recent_meetings)
    risk_analysis = risk_detector.get_comprehensive_risk_analysis()
    
    # Get trend analysis
    trend_analyzer = TrendAnalyzer(recent_meetings)
    trend_analysis = trend_analyzer.get_comprehensive_analysis()
    
    context = {
        'health_index': health_index,
        'risk_analysis': risk_analysis,
        'trend_analysis': trend_analysis,
        'recent_meetings': recent_meetings,
    }
    
    return render(request, 'meetings/team_health.html', context)


def delete_meeting(request, pk):
    """Delete a meeting"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    if request.method == 'POST':
        meeting_title = meeting.title
        meeting.delete()
        messages.success(request, f'Successfully deleted meeting: {meeting_title}')
        return redirect('meeting_list')
    
    # If GET request, show confirmation
    return render(request, 'meetings/delete_confirm.html', {'meeting': meeting})


def executive_dashboard(request):
    """
    Executive-level dashboard with AI insights and recommendations
    """
    meetings = Meeting.objects.all().order_by('-date')
    
    if meetings.count() < 1:
        messages.info(request, 'Upload at least one meeting to see executive insights')
        return redirect('upload_transcript')
    
    # Get recent meetings for analysis (last 5)
    recent_meetings = list(meetings[:5])
    
    # Generate insights
    insights_generator = TeamInsightsGenerator(recent_meetings)
    
    # AI Insight Banner
    ai_insight = insights_generator.generate_ai_insight_banner()
    
    executive_summary = insights_generator.generate_executive_summary()
    key_strengths = insights_generator.identify_key_strengths()
    primary_risks = insights_generator.identify_primary_risks()
    recommended_actions = insights_generator.generate_recommended_actions()
    top_priorities = insights_generator.get_top_priorities()
    
    # Calculate Team Health Score
    health_index = calculate_team_health_index(recent_meetings) if len(recent_meetings) >= 2 else None
    
    # Get trend data
    if len(recent_meetings) >= 2:
        trend_analyzer = TrendAnalyzer(recent_meetings)
        trends = trend_analyzer.get_comprehensive_analysis()
    else:
        trends = None
    
    context = {
        'meetings': recent_meetings,
        'ai_insight': ai_insight,
        'executive_summary': executive_summary,
        'key_strengths': key_strengths,
        'primary_risks': primary_risks,
        'recommended_actions': recommended_actions,
        'top_priorities': top_priorities,
        'health_index': health_index,
        'trends': trends,
        'total_meetings': meetings.count(),
    }
    
    return render(request, 'meetings/executive_dashboard.html', context)


def meeting_comparison(request):
    """
    Compare two meetings side-by-side
    """
    all_meetings = Meeting.objects.all().order_by('-date')
    
    meeting1_id = request.GET.get('meeting1')
    meeting2_id = request.GET.get('meeting2')
    
    context = {
        'all_meetings': all_meetings,
        'meeting1_id': int(meeting1_id) if meeting1_id else None,
        'meeting2_id': int(meeting2_id) if meeting2_id else None,
    }
    
    if meeting1_id and meeting2_id:
        meeting1 = get_object_or_404(Meeting, pk=meeting1_id)
        meeting2 = get_object_or_404(Meeting, pk=meeting2_id)
        
        # Calculate changes
        sentiment_change = (meeting2.avg_sentiment or 0) - (meeting1.avg_sentiment or 0)
        balance_change = (meeting2.participation_balance or 0) - (meeting1.participation_balance or 0)
        message_change = meeting2.total_messages - meeting1.total_messages
        word_change = meeting2.total_words - meeting1.total_words
        
        # Generate comparison summary
        comparison_summary = generate_comparison_summary(meeting1, meeting2, sentiment_change, balance_change)
        
        # Speaker-level comparison
        speaker_comparison = compare_speakers(meeting1, meeting2)
        
        # Sentiment distribution
        meeting1_sentiment_data = get_sentiment_distribution(meeting1)
        meeting2_sentiment_data = get_sentiment_distribution(meeting2)
        
        context.update({
            'meeting1': meeting1,
            'meeting2': meeting2,
            'sentiment_change': sentiment_change,
            'balance_change': balance_change,
            'message_change': message_change,
            'word_change': word_change,
            'comparison_summary': comparison_summary,
            'speaker_comparison': speaker_comparison,
            'meeting1_sentiment_data': meeting1_sentiment_data,
            'meeting2_sentiment_data': meeting2_sentiment_data,
        })
    
    return render(request, 'meetings/meeting_comparison.html', context)


def generate_comparison_summary(meeting1, meeting2, sentiment_change, balance_change):
    """Generate AI summary of comparison"""
    parts = []
    
    # Sentiment comparison
    if sentiment_change > 0.1:
        parts.append(f"Team sentiment improved significantly between meetings (+{sentiment_change:.2f})")
    elif sentiment_change < -0.1:
        parts.append(f"Team sentiment declined between meetings ({sentiment_change:.2f})")
    else:
        parts.append("Team sentiment remained relatively stable")
    
    # Balance comparison
    if balance_change > 0.1:
        parts.append("participation became more balanced")
    elif balance_change < -0.1:
        parts.append("participation became more imbalanced")
    else:
        parts.append("participation balance stayed consistent")
    
    # Communication volume
    msg_diff = meeting2.total_messages - meeting1.total_messages
    if msg_diff > 20:
        parts.append(f"Communication volume increased substantially (+{msg_diff} messages)")
    elif msg_diff < -20:
        parts.append(f"Communication volume decreased ({msg_diff} messages)")
    
    summary = f"{parts[0]}, while {parts[1]}"
    if len(parts) > 2:
        summary += f". {parts[2]}"
    
    return summary + "."


def compare_speakers(meeting1, meeting2):
    """Compare speaker participation across meetings"""
    # Get all speakers from both meetings
    all_speakers = set()
    meeting1_metrics = {m.speaker.name: m for m in meeting1.metrics.all()}
    meeting2_metrics = {m.speaker.name: m for m in meeting2.metrics.all()}
    
    all_speakers.update(meeting1_metrics.keys())
    all_speakers.update(meeting2_metrics.keys())
    
    comparison = {}
    
    for speaker in all_speakers:
        m1 = meeting1_metrics.get(speaker)
        m2 = meeting2_metrics.get(speaker)
        
        change = None
        if m1 and m2:
            change = m2.participation_percentage - m1.participation_percentage
        
        comparison[speaker] = {
            'meeting1': m1,
            'meeting2': m2,
            'change': change
        }
    
    return comparison


def get_sentiment_distribution(meeting):
    """Get sentiment distribution for a meeting"""
    messages = meeting.messages.all()
    
    positive = sum(1 for m in messages if m.sentiment_score and m.sentiment_score > 0.05)
    negative = sum(1 for m in messages if m.sentiment_score and m.sentiment_score < -0.05)
    neutral = len(messages) - positive - negative
    
    return {
        'positive': positive,
        'neutral': neutral,
        'negative': negative
    }


def risk_filter(request):
    """
    Filter and display risks by severity and type
    """
    meetings = Meeting.objects.all().order_by('-date')
    
    # Get filter parameters
    selected_severity = request.GET.get('severity', '')
    selected_type = request.GET.get('risk_type', '')
    selected_range = request.GET.get('range', '5')
    
    # Apply meeting range filter
    if selected_range == 'all':
        filtered_meetings = list(meetings)
    else:
        filtered_meetings = list(meetings[:int(selected_range)])
    
    if len(filtered_meetings) < 2:
        messages.info(request, 'Need at least 2 meetings for risk analysis')
        return redirect('meeting_list')
    
    # Get all risks
    risk_detector = RiskDetector(filtered_meetings)
    all_risks_data = risk_detector.get_comprehensive_risk_analysis()
    
    # Compile all risks into a list
    all_risks = []
    
    # Conflict risk
    if all_risks_data['conflict_risk']['risk_level'] != 'none':
        all_risks.append({
            'type': 'Team Conflict',
            'level': all_risks_data['conflict_risk']['risk_level'],
            'score': all_risks_data['conflict_risk']['risk_score'],
            'explanation': ', '.join(all_risks_data['conflict_risk']['indicators']),
            'impact': 'May lead to decreased collaboration and team cohesion',
            'recommendation': all_risks_data['conflict_risk']['recommendation'],
            'category': 'conflict'
        })
    
    # Burnout risk
    if all_risks_data['burnout_risk']['risk_level'] != 'none':
        all_risks.append({
            'type': 'Team Burnout',
            'level': all_risks_data['burnout_risk']['risk_level'],
            'score': all_risks_data['burnout_risk']['risk_score'],
            'explanation': ', '.join(all_risks_data['burnout_risk']['indicators']),
            'impact': 'Could result in reduced productivity and team turnover',
            'recommendation': all_risks_data['burnout_risk']['recommendation'],
            'category': 'burnout'
        })
    
    # Dominance issues
    if all_risks_data['dominance_issues']['risk_level'] != 'none':
        all_risks.append({
            'type': 'Conversation Dominance',
            'level': all_risks_data['dominance_issues']['risk_level'],
            'score': all_risks_data['dominance_issues']['risk_score'],
            'explanation': ', '.join(all_risks_data['dominance_issues']['indicators']),
            'impact': 'Quieter team members may feel unheard or disengaged',
            'recommendation': all_risks_data['dominance_issues']['recommendation'],
            'category': 'dominance'
        })
    
    # Disengagement
    if all_risks_data['disengagement_risk']['risk_level'] != 'none':
        all_risks.append({
            'type': 'Team Disengagement',
            'level': all_risks_data['disengagement_risk']['risk_level'],
            'score': 50,
            'explanation': all_risks_data['disengagement_risk']['recommendation'],
            'impact': 'May indicate burnout or role dissatisfaction',
            'recommendation': all_risks_data['disengagement_risk']['recommendation'],
            'category': 'disengagement'
        })
    
    # Apply filters
    filtered_risks = all_risks
    
    if selected_severity:
        filtered_risks = [r for r in filtered_risks if r['level'] == selected_severity]
    
    if selected_type:
        filtered_risks = [r for r in filtered_risks if r['category'] == selected_type]
    
    # Count risks by severity
    high_risk_count = sum(1 for r in all_risks if r['level'] == 'high')
    medium_risk_count = sum(1 for r in all_risks if r['level'] == 'medium')
    low_risk_count = sum(1 for r in all_risks if r['level'] == 'low')
    
    context = {
        'filtered_risks': filtered_risks,
        'selected_severity': selected_severity,
        'selected_type': selected_type,
        'selected_range': selected_range,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'total_meetings': len(filtered_meetings),
    }
    
    return render(request, 'meetings/risk_filter.html', context)


def export_meeting_pdf(request, pk):
    """Export single meeting as PDF"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Generate PDF
    generator = MeetingReportGenerator(meeting)
    pdf_data = generator.generate_report()
    
    # Create response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    filename = f"TeamPulse_Meeting_{meeting.title.replace(' ', '_')}_{meeting.date.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_meeting_excel(request, pk):
    """Export single meeting as Excel"""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    # Generate Excel
    exporter = MeetingExcelExporter(meeting)
    excel_data = exporter.generate_excel()
    
    # Create response
    response = HttpResponse(
        excel_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"TeamPulse_Meeting_{meeting.title.replace(' ', '_')}_{meeting.date.strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_team_health_pdf(request):
    """Export team health report as PDF"""
    meetings = Meeting.objects.all().order_by('-date')[:10]
    
    if meetings.count() < 2:
        messages.error(request, 'Need at least 2 meetings to generate team health report')
        return redirect('executive_dashboard')
    
    # Generate PDF
    generator = TeamHealthReportGenerator(list(meetings))
    pdf_data = generator.generate_report()
    
    # Create response
    response = HttpResponse(pdf_data, content_type='application/pdf')
    filename = f"TeamPulse_TeamHealth_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def export_team_health_excel(request):
    """Export team health data as Excel"""
    meetings = Meeting.objects.all().order_by('-date')[:10]
    
    if meetings.count() < 2:
        messages.error(request, 'Need at least 2 meetings to generate team health report')
        return redirect('executive_dashboard')
    
    # Generate Excel
    exporter = TeamHealthExcelExporter(list(meetings))
    excel_data = exporter.generate_excel()
    
    # Create response
    response = HttpResponse(
        excel_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"TeamPulse_TeamHealth_{datetime.now().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def send_email_digest(request):
    """
    Send email digest (for testing - in production use Celery for scheduled tasks)
    """
    if request.method == 'POST':
        recipient_email = request.POST.get('email')
        recipient_name = request.POST.get('name', 'Team Lead')
        
        if not recipient_email:
            messages.error(request, 'Email address is required')
            return redirect('executive_dashboard')
        
        # Generate and send digest
        digest = EmailDigestGenerator(recipient_email, recipient_name)
        success, message = digest.send_weekly_digest()
        
        if success:
            messages.success(request, f'Email digest sent successfully to {recipient_email}')
        else:
            messages.error(request, f'Failed to send email: {message}')
        
        return redirect('executive_dashboard')
    
    return render(request, 'meetings/send_digest.html')
