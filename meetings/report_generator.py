from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from .models import Meeting
from .insights_generator import TeamInsightsGenerator
from .trend_analyzer import TrendAnalyzer
from .risk_detector import RiskDetector
from .utils import calculate_team_health_index  


class MeetingReportGenerator:
    """
    Generate professional PDF reports for meeting analysis
    """
    
    def __init__(self, meeting):
        self.meeting = meeting
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12
        )
    
    def generate_report(self):
        """Generate complete meeting report"""
        # Title Page
        self._add_title()
        self._add_meeting_info()
        
        # Executive Summary
        self._add_executive_summary()
        
        # Key Metrics
        self._add_key_metrics()
        
        # Speaker Analysis
        self._add_speaker_analysis()
        
        # Recommendations
        self._add_recommendations()
        
        # Build PDF
        self.doc.build(self.story)
        
        # Get PDF data
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_data
    
    def _add_title(self):
        """Add report title"""
        title = Paragraph("TeamPulse AI", self.title_style)
        subtitle = Paragraph("Meeting Analysis Report", self.body_style)
        
        self.story.append(title)
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def _add_meeting_info(self):
        """Add meeting basic information"""
        data = [
            ['Meeting Title:', self.meeting.title],
            ['Date:', self.meeting.date.strftime('%B %d, %Y at %I:%M %p')],
            ['Duration:', f"{self.meeting.duration_minutes} minutes" if self.meeting.duration_minutes else 'N/A'],
            ['Total Messages:', str(self.meeting.total_messages)],
            ['Total Words:', str(self.meeting.total_words)],
            ['Overall Sentiment:', self.meeting.sentiment_label.title()],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.4 * inch))
    
    def _add_executive_summary(self):
        """Add executive summary section"""
        heading = Paragraph("Executive Summary", self.heading_style)
        self.story.append(heading)
        
        # Generate summary
        insights_gen = TeamInsightsGenerator([self.meeting])
        summary = insights_gen.generate_executive_summary()
        
        summary_text = Paragraph(summary, self.body_style)
        self.story.append(summary_text)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def _add_key_metrics(self):
        """Add key metrics section"""
        heading = Paragraph("Key Metrics", self.heading_style)
        self.story.append(heading)
        
        # Metrics table
        sentiment_score = (self.meeting.avg_sentiment or 0) if self.meeting.avg_sentiment else 0
        sentiment_percentage = ((sentiment_score + 1) / 2) * 100
        
        data = [
            ['Metric', 'Value', 'Status'],
            ['Average Sentiment', f"{sentiment_score:.2f}", self._get_status(sentiment_score, 0.2, -0.1)],
            ['Participation Balance', f"{self.meeting.participation_balance:.2f}", self._get_status(self.meeting.participation_balance, 0.65, 0.4)],
            ['Messages per Person', f"{self.meeting.total_messages / max(self.meeting.metrics.count(), 1):.1f}", 'N/A'],
            ['Words per Person', f"{self.meeting.total_words / max(self.meeting.metrics.count(), 1):.1f}", 'N/A'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.white])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def _add_speaker_analysis(self):
        """Add speaker participation analysis"""
        heading = Paragraph("Speaker Participation Analysis", self.heading_style)
        self.story.append(heading)
        
        metrics = self.meeting.metrics.all().order_by('-participation_percentage')
        
        if not metrics:
            no_data = Paragraph("No speaker data available.", self.body_style)
            self.story.append(no_data)
            return
        
        # Speaker table
        data = [['Speaker', 'Messages', 'Words', 'Participation %', 'Engagement', 'Avg Sentiment']]
        
        for metric in metrics:
            data.append([
                metric.speaker.name,
                str(metric.total_messages),
                str(metric.total_words),
                f"{metric.participation_percentage:.1f}%",
                f"{metric.engagement_score:.0f}/100",
                f"{metric.avg_sentiment:.2f}" if metric.avg_sentiment else 'N/A'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1f2937')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.white])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def _add_recommendations(self):
        """Add AI recommendations"""
        heading = Paragraph("AI-Generated Recommendations", self.heading_style)
        self.story.append(heading)
        
        # Generate recommendations
        insights_gen = TeamInsightsGenerator([self.meeting])
        actions = insights_gen.generate_recommended_actions()
        
        if not actions:
            no_recs = Paragraph("No specific recommendations at this time.", self.body_style)
            self.story.append(no_recs)
            return
        
        for i, action in enumerate(actions[:3], 1):
            action_title = Paragraph(f"<b>{i}. {action['action']}</b>", self.body_style)
            self.story.append(action_title)
            
            reason = Paragraph(f"<i>Reason:</i> {action['reason']}", self.body_style)
            self.story.append(reason)
            
            impact = Paragraph(f"<i>Expected Impact:</i> {action['expected_impact']}", self.body_style)
            self.story.append(impact)
            
            self.story.append(Spacer(1, 0.15 * inch))
        
        # Footer
        self.story.append(Spacer(1, 0.5 * inch))
        footer = Paragraph(
            f"<i>Report generated by TeamPulse AI on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            ParagraphStyle('Footer', parent=self.body_style, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)
        )
        self.story.append(footer)
    
    def _get_status(self, value, good_threshold, bad_threshold):
        """Determine status based on thresholds"""
        if value >= good_threshold:
            return '✓ Good'
        elif value <= bad_threshold:
            return '✗ Needs Attention'
        else:
            return '~ Moderate'


class TeamHealthReportGenerator:
    """
    Generate comprehensive team health reports across multiple meetings
    """
    
    def __init__(self, meetings):
        self.meetings = meetings
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Set up styles (similar to MeetingReportGenerator)
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12
        )
    
    def generate_report(self):
        """Generate team health report"""
        # Title
        self._add_title()
        
        # Executive Summary
        self._add_executive_summary()
        
        # Team Health Score
        self._add_team_health_score()

        def _add_team_health_score(self):
        # REMOVED: from .views import calculate_team_health_index
        # It's already imported at the top of the file
        
           heading = Paragraph("Team Health Index", self.heading_style)
           self.story.append(heading)
        
        health_index = calculate_team_health_index(self.meetings)
        
        score_text = Paragraph(
            f"<b>Overall Score: {health_index['score']}/100 ({health_index['level'].upper()})</b>",
            self.body_style
        )
        self.story.append(score_text)
        self.story.append(Spacer(1, 0.2 * inch))

        
        # Trends
        self._add_trends()
        
        # Risks
        self._add_risks()
        
        # Priority Actions
        self._add_priority_actions()
        
        # Build PDF
        self.doc.build(self.story)
        
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_data
    
    def _add_title(self):
        """Add title"""
        title = Paragraph("TeamPulse AI", self.title_style)
        subtitle = Paragraph("Team Health Report", self.body_style)
        date_range = Paragraph(
            f"Analysis Period: {self.meetings[-1].date.strftime('%B %d, %Y')} - {self.meetings[0].date.strftime('%B %d, %Y')}",
            self.body_style
        )
        
        self.story.append(title)
        self.story.append(subtitle)
        self.story.append(date_range)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def _add_executive_summary(self):
        """Add executive summary"""
        heading = Paragraph("Executive Summary", self.heading_style)
        self.story.append(heading)
        
        insights_gen = TeamInsightsGenerator(self.meetings)
        summary = insights_gen.generate_executive_summary()
        
        summary_para = Paragraph(summary, self.body_style)
        self.story.append(summary_para)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def _add_team_health_score(self):
        """Add team health score"""
        from .views import calculate_team_health_index
        
        heading = Paragraph("Team Health Index", self.heading_style)
        self.story.append(heading)
        
        health_index = calculate_team_health_index(self.meetings)
        
        score_text = Paragraph(
            f"<b>Overall Score: {health_index['score']}/100 ({health_index['level'].upper()})</b>",
            self.body_style
        )
        self.story.append(score_text)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def _add_trends(self):
        """Add trend analysis"""
        heading = Paragraph("Trend Analysis", self.heading_style)
        self.story.append(heading)
        
        trend_analyzer = TrendAnalyzer(self.meetings)
        trends = trend_analyzer.get_comprehensive_analysis()
        
        trend_text = f"""
        <b>Sentiment:</b> {trends['sentiment']['trend'].title()} ({trends['sentiment']['change_percentage']:.1f}% change)<br/>
        <b>Participation:</b> {trends['participation']['trend'].title()} ({trends['participation']['change_percentage']:.1f}% change)<br/>
        <b>Engagement:</b> {trends['engagement']['trend'].title()} ({trends['engagement']['change_percentage']:.1f}% change)<br/>
        <b>Communication Volume:</b> {trends['message_volume']['trend'].title()} ({trends['message_volume']['change_percentage']:.1f}% change)
        """
        
        trend_para = Paragraph(trend_text, self.body_style)
        self.story.append(trend_para)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def _add_risks(self):
        """Add risk analysis"""
        heading = Paragraph("Risk Assessment", self.heading_style)
        self.story.append(heading)
        
        risk_detector = RiskDetector(self.meetings)
        risks = risk_detector.get_comprehensive_risk_analysis()
        
        risk_text = f"""
        <b>Conflict Risk:</b> {risks['conflict_risk']['risk_level'].upper()} (Score: {risks['conflict_risk']['risk_score']})<br/>
        <b>Burnout Risk:</b> {risks['burnout_risk']['risk_level'].upper()} (Score: {risks['burnout_risk']['risk_score']})<br/>
        <b>Dominance Issues:</b> {risks['dominance_issues']['risk_level'].upper()} (Score: {risks['dominance_issues']['risk_score']})
        """
        
        risk_para = Paragraph(risk_text, self.body_style)
        self.story.append(risk_para)
        self.story.append(Spacer(1, 0.2 * inch))
    
    def _add_priority_actions(self):
        """Add priority actions"""
        heading = Paragraph("Top Priority Actions", self.heading_style)
        self.story.append(heading)
        
        insights_gen = TeamInsightsGenerator(self.meetings)
        priorities = insights_gen.get_top_priorities()
        
        if priorities:
            for priority in priorities:
                action_text = f"<b>{priority['rank']}. {priority['title']}</b> ({priority['severity']})<br/>{priority['description']}<br/><i>Action: {priority['action']}</i>"
                action_para = Paragraph(action_text, self.body_style)
                self.story.append(action_para)
                self.story.append(Spacer(1, 0.15 * inch))
        else:
            no_priorities = Paragraph("No urgent priorities detected.", self.body_style)
            self.story.append(no_priorities)
        
        # Footer
        self.story.append(Spacer(1, 0.5 * inch))
        footer = Paragraph(
            f"<i>Report generated by TeamPulse AI on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            ParagraphStyle('Footer', parent=self.body_style, fontSize=9, textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER)
        )
        self.story.append(footer)
