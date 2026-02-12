from typing import Dict, List
from .models import Meeting, MeetingMetrics
from .trend_analyzer import TrendAnalyzer
import statistics


class RiskDetector:
    """
    Detect early warning signs of team dysfunction
    """
    
    # Risk thresholds
    SENTIMENT_DECLINE_THRESHOLD = -15  # % decline
    PARTICIPATION_IMBALANCE_THRESHOLD = 0.5  # balance score
    ENGAGEMENT_DECLINE_THRESHOLD = -20  # % decline
    NEGATIVE_SENTIMENT_THRESHOLD = -0.3  # absolute score
    
    def __init__(self, meetings: List[Meeting]):
        self.meetings = sorted(meetings, key=lambda m: m.date)
        self.trend_analyzer = TrendAnalyzer(meetings)
    
    def detect_conflict_risk(self) -> Dict:
        """
        Detect signs of rising team conflict
        
        Indicators:
        - Declining sentiment
        - Increasing negative tone
        - Decreasing participation balance
        """
        if len(self.meetings) < 3:
            return {
                'risk_level': 'unknown',
                'risk_score': 0,
                'indicators': [],
                'recommendation': 'Need more meetings for analysis'
            }
        
        sentiment_trend = self.trend_analyzer.analyze_sentiment_trend()
        participation_trend = self.trend_analyzer.analyze_participation_trend()
        
        indicators = []
        risk_score = 0
        
        # Check sentiment decline
        if sentiment_trend['trend'] == 'declining':
            if sentiment_trend['change_percentage'] < self.SENTIMENT_DECLINE_THRESHOLD:
                indicators.append(f"Sentiment declined by {abs(sentiment_trend['change_percentage']):.1f}%")
                risk_score += 30
        
        # Check negative sentiment
        recent_sentiment = sentiment_trend['current_avg']
        if recent_sentiment < self.NEGATIVE_SENTIMENT_THRESHOLD:
            indicators.append(f"Recent sentiment is negative ({recent_sentiment:.2f})")
            risk_score += 25
        
        # Check participation imbalance
        recent_balance = participation_trend['current_balance']
        if recent_balance < self.PARTICIPATION_IMBALANCE_THRESHOLD:
            indicators.append(f"Low participation balance ({recent_balance:.2f})")
            risk_score += 20
        
        # Check if imbalance is worsening
        if participation_trend['trend'] == 'declining':
            indicators.append("Participation becoming more unbalanced")
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'high'
            recommendation = "⚠️ URGENT: Schedule 1-on-1s to address team tensions. Consider conflict resolution facilitation."
        elif risk_score >= 30:
            risk_level = 'medium'
            recommendation = "⚠️ Monitor closely. Consider team retrospective to surface concerns."
        elif risk_score > 0:
            risk_level = 'low'
            recommendation = "Minor concerns detected. Keep monitoring trends."
        else:
            risk_level = 'none'
            recommendation = "No conflict risks detected. Team communication appears healthy."
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'indicators': indicators,
            'recommendation': recommendation
        }
    
    def detect_burnout_risk(self) -> Dict:
        """
        Detect signs of team burnout or fatigue
        
        Indicators:
        - Declining engagement
        - Decreasing message volume
        - Increasingly negative sentiment
        """
        if len(self.meetings) < 3:
            return {
                'risk_level': 'unknown',
                'risk_score': 0,
                'indicators': [],
                'recommendation': 'Need more meetings for analysis'
            }
        
        engagement_trend = self.trend_analyzer.analyze_engagement_trend()
        message_trend = self.trend_analyzer.analyze_message_volume_trend()
        sentiment_trend = self.trend_analyzer.analyze_sentiment_trend()
        
        indicators = []
        risk_score = 0
        
        # Check engagement decline
        if engagement_trend['trend'] == 'declining':
            if engagement_trend['change_percentage'] < self.ENGAGEMENT_DECLINE_THRESHOLD:
                indicators.append(f"Engagement dropped {abs(engagement_trend['change_percentage']):.1f}%")
                risk_score += 35
        
        # Check message volume decline
        if message_trend['trend'] == 'decreasing':
            if message_trend['change_percentage'] < -20:
                indicators.append(f"Communication volume down {abs(message_trend['change_percentage']):.1f}%")
                risk_score += 25
        
        # Check sentiment decline
        if sentiment_trend['trend'] == 'declining':
            indicators.append("Team sentiment declining")
            risk_score += 20
        
        # Check recent engagement absolute level
        if engagement_trend['current_avg'] < 40:
            indicators.append(f"Low team engagement ({engagement_trend['current_avg']:.1f}/100)")
            risk_score += 20
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = 'high'
            recommendation = "🔥 URGENT: Team showing burnout signs. Consider workload reduction and wellness check-ins."
        elif risk_score >= 35:
            risk_level = 'medium'
            recommendation = "⚠️ Watch for burnout. Consider lighter meeting schedule and workload assessment."
        elif risk_score > 0:
            risk_level = 'low'
            recommendation = "Some fatigue indicators. Monitor team energy levels."
        else:
            risk_level = 'none'
            recommendation = "No burnout risks detected. Team engagement appears healthy."
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'indicators': indicators,
            'recommendation': recommendation
        }
    
    def detect_dominance_issues(self) -> Dict:
        """
        Detect if 1-2 people are dominating conversations
        """
        if not self.meetings:
            return {
                'risk_level': 'unknown',
                'risk_score': 0,
                'indicators': [],
                'dominant_speakers': []
            }
        
        # Analyze most recent meeting
        recent_meeting = self.meetings[-1]
        metrics = recent_meeting.metrics.order_by('-participation_percentage').all()
        
        if len(metrics) < 2:
            return {
                'risk_level': 'unknown',
                'risk_score': 0,
                'indicators': [],
                'dominant_speakers': []
            }
        
        indicators = []
        risk_score = 0
        dominant_speakers = []
        
        # Check if top speaker dominates
        top_participation = metrics[0].participation_percentage
        if top_participation > 50:
            indicators.append(f"{metrics[0].speaker.name} speaks {top_participation:.1f}% of the time")
            dominant_speakers.append(metrics[0].speaker.name)
            risk_score += 40
        elif top_participation > 40:
            indicators.append(f"{metrics[0].speaker.name} dominates conversation ({top_participation:.1f}%)")
            dominant_speakers.append(metrics[0].speaker.name)
            risk_score += 25
        
        # Check if top 2 speakers dominate
        if len(metrics) >= 2:
            top_two_participation = metrics[0].participation_percentage + metrics[1].participation_percentage
            if top_two_participation > 75:
                indicators.append(f"Top 2 speakers control {top_two_participation:.1f}% of conversation")
                risk_score += 20
        
        # Check participation balance
        if recent_meeting.participation_balance < 0.5:
            indicators.append(f"Very unbalanced participation (score: {recent_meeting.participation_balance:.2f})")
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'high'
            recommendation = "⚠️ Conversation dominated by few people. Actively solicit input from quieter members."
        elif risk_score >= 30:
            risk_level = 'medium'
            recommendation = "⚠️ Consider round-robin speaking order or explicit turn-taking."
        elif risk_score > 0:
            risk_level = 'low'
            recommendation = "Minor imbalance detected. Encourage broader participation."
        else:
            risk_level = 'none'
            recommendation = "Participation appears balanced across team members."
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'indicators': indicators,
            'dominant_speakers': dominant_speakers,
            'recommendation': recommendation
        }
    
    def detect_disengagement(self) -> Dict:
        """
        Detect specific individuals who may be disengaging
        """
        if len(self.meetings) < 3:
            return {
                'risk_level': 'unknown',
                'at_risk_speakers': [],
                'recommendation': 'Need more meetings for analysis'
            }
        
        # Look at recent 3 meetings
        recent_meetings = self.meetings[-3:]
        
        # Track each speaker's engagement trend
        speaker_engagement = {}
        
        for meeting in recent_meetings:
            for metric in meeting.metrics.all():
                speaker_name = metric.speaker.name
                if speaker_name not in speaker_engagement:
                    speaker_engagement[speaker_name] = []
                
                speaker_engagement[speaker_name].append({
                    'engagement': metric.engagement_score,
                    'participation': metric.participation_percentage,
                    'date': meeting.date
                })
        
        at_risk_speakers = []
        
        for speaker_name, engagements in speaker_engagement.items():
            if len(engagements) >= 2:
                # Check for declining trend
                scores = [e['engagement'] for e in engagements]
                
                # Simple decline detection
                if len(scores) >= 2:
                    first_half_avg = statistics.mean(scores[:len(scores)//2])
                    second_half_avg = statistics.mean(scores[len(scores)//2:])
                    
                    decline_pct = ((second_half_avg - first_half_avg) / (first_half_avg + 0.001)) * 100
                    
                    if decline_pct < -25 or second_half_avg < 35:
                        at_risk_speakers.append({
                            'name': speaker_name,
                            'current_engagement': round(second_half_avg, 1),
                            'decline_percentage': round(decline_pct, 1)
                        })
        
        if len(at_risk_speakers) >= 2:
            risk_level = 'high'
            recommendation = f"⚠️ Multiple team members showing disengagement. Schedule 1-on-1 check-ins."
        elif len(at_risk_speakers) == 1:
            risk_level = 'medium'
            recommendation = f"⚠️ {at_risk_speakers[0]['name']} may be disengaging. Consider a check-in."
        else:
            risk_level = 'none'
            recommendation = "All team members appear engaged."
        
        return {
            'risk_level': risk_level,
            'at_risk_speakers': at_risk_speakers,
            'recommendation': recommendation
        }
    
    def get_comprehensive_risk_analysis(self) -> Dict:
        """
        Run all risk detections and return comprehensive report
        """
        return {
            'conflict_risk': self.detect_conflict_risk(),
            'burnout_risk': self.detect_burnout_risk(),
            'dominance_issues': self.detect_dominance_issues(),
            'disengagement_risk': self.detect_disengagement(),
            'overall_risk_score': self._calculate_overall_risk()
        }
    
    def _calculate_overall_risk(self) -> Dict:
        """
        Calculate overall team health risk
        """
        conflict = self.detect_conflict_risk()
        burnout = self.detect_burnout_risk()
        dominance = self.detect_dominance_issues()
        
        total_score = (
            conflict['risk_score'] * 0.4 +  # Conflict is most serious
            burnout['risk_score'] * 0.35 +  # Burnout is very serious
            dominance['risk_score'] * 0.25  # Dominance is concerning
        )
        
        if total_score >= 50:
            level = 'critical'
            color = 'danger'
        elif total_score >= 35:
            level = 'high'
            color = 'warning'
        elif total_score >= 15:
            level = 'medium'
            color = 'info'
        else:
            level = 'low'
            color = 'success'
        
        return {
            'score': round(total_score, 1),
            'level': level,
            'color': color
        }
    