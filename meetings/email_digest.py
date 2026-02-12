from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Meeting
from .insights_generator import TeamInsightsGenerator
from .utils import calculate_team_health_index
from datetime import datetime, timedelta


class EmailDigestGenerator:
    """
    Generate and send weekly team health email digests
    """
    
    def __init__(self, recipient_email, recipient_name="Team Lead"):
        self.recipient_email = recipient_email
        self.recipient_name = recipient_name
    
    def send_weekly_digest(self):
        """Send weekly team health digest"""
        # Get recent meetings (last 30 days OR latest 5 meetings if none in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_meetings = Meeting.objects.filter(date__gte=thirty_days_ago).order_by('-date')
        
        # If no meetings in last 30 days, get the 5 most recent meetings
        if recent_meetings.count() == 0:
            recent_meetings = Meeting.objects.all().order_by('-date')[:5]
        
        if recent_meetings.count() == 0:
            return False, "No meetings available to generate digest"
        
        # FIXED: Convert QuerySet to list BEFORE passing to insights generator
        meetings_list = list(recent_meetings)
        
        # Generate insights
        insights_gen = TeamInsightsGenerator(meetings_list)
        
        executive_summary = insights_gen.generate_executive_summary()
        key_strengths = insights_gen.identify_key_strengths()
        primary_risks = insights_gen.identify_primary_risks()
        top_priorities = insights_gen.get_top_priorities()
        
        # Calculate health score
        if len(meetings_list) >= 2:
            health_index = calculate_team_health_index(meetings_list)
        else:
            health_index = None
        
        # Determine date range for the digest
        if len(meetings_list) > 0:
            oldest_meeting = meetings_list[-1]  # FIXED: Use list indexing
            newest_meeting = meetings_list[0]   # FIXED: Use list indexing
            week_start = oldest_meeting.date.strftime('%B %d, %Y')
            week_end = newest_meeting.date.strftime('%B %d, %Y')
        else:
            week_start = thirty_days_ago.strftime('%B %d, %Y')
            week_end = datetime.now().strftime('%B %d, %Y')
        
        # Prepare context
        context = {
            'recipient_name': self.recipient_name,
            'week_start': week_start,
            'week_end': week_end,
            'meeting_count': len(meetings_list),
            'meetings': meetings_list,
            'executive_summary': executive_summary,
            'key_strengths': key_strengths,
            'primary_risks': primary_risks[:3],
            'top_priorities': top_priorities,
            'health_index': health_index,
        }
        
        # Render email
        html_content = render_to_string('meetings/email_digest.html', context)
        text_content = self._generate_text_content(context)
        
        # Send email
        subject = f"TeamPulse AI - Team Health Digest ({week_start} - {week_end})"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.recipient_email]
        )
        
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send()
            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)
    
    def _generate_text_content(self, context):
        """Generate plain text version of email"""
        text = f"""
TeamPulse AI - Team Health Digest

Hello {context['recipient_name']},

Here's your team collaboration summary for {context['week_start']} - {context['week_end']}

EXECUTIVE SUMMARY:
{context['executive_summary']}

"""
        
        if context['health_index']:
            text += f"\nTEAM HEALTH SCORE: {context['health_index']['score']}/100 ({context['health_index']['level'].upper()})\n"
        
        if context['key_strengths']:
            text += "\nKEY STRENGTHS:\n"
            for strength in context['key_strengths']:
                text += f"✓ {strength}\n"
        
        if context['primary_risks']:
            text += "\nPRIMARY RISKS:\n"
            for risk in context['primary_risks']:
                text += f"⚠ {risk['type']}: {risk['explanation']}\n"
        
        if context['top_priorities']:
            text += "\nTOP PRIORITY ACTIONS:\n"
            for priority in context['top_priorities']:
                text += f"{priority['rank']}. {priority['title']} - {priority['action']}\n"
        
        text += f"\n\nAnalyzed {context['meeting_count']} meeting(s).\n"
        text += "\nView full dashboard: http://127.0.0.1:8000\n"
        text += "\n---\nThis is an automated email from TeamPulse AI\n"
        
        return text
    