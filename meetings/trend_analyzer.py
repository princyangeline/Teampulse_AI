from django.db.models import Avg, Count, Sum
from typing import Dict, List, Optional
from datetime import timedelta
from .models import Meeting, MeetingMetrics
import statistics


class TrendAnalyzer:
    """
    Analyzes trends across multiple meetings to detect patterns
    """
    
    def __init__(self, meetings: List[Meeting]):
        """
        Initialize with a list of meetings (ordered by date)
        """
        self.meetings = sorted(meetings, key=lambda m: m.date)
    
    def analyze_sentiment_trend(self) -> Dict:
        """
        Analyze how sentiment changes over time
        
        Returns:
            {
                'trend': 'improving' | 'declining' | 'stable',
                'change_percentage': float,
                'current_avg': float,
                'previous_avg': float,
                'data_points': [{'date': str, 'sentiment': float}]
            }
        """
        if len(self.meetings) < 2:
            return {
                'trend': 'insufficient_data',
                'change_percentage': 0.0,
                'current_avg': 0.0,
                'previous_avg': 0.0,
                'data_points': []
            }
        
        data_points = [
            {
                'date': meeting.date.strftime('%Y-%m-%d'),
                'sentiment': meeting.avg_sentiment or 0.0
            }
            for meeting in self.meetings
        ]
        
        # Compare recent half vs earlier half
        mid_point = len(self.meetings) // 2
        earlier_meetings = self.meetings[:mid_point]
        recent_meetings = self.meetings[mid_point:]
        
        earlier_avg = statistics.mean([m.avg_sentiment or 0.0 for m in earlier_meetings])
        recent_avg = statistics.mean([m.avg_sentiment or 0.0 for m in recent_meetings])
        
        change_pct = ((recent_avg - earlier_avg) / abs(earlier_avg + 0.001)) * 100
        
        # Determine trend
        if change_pct > 10:
            trend = 'improving'
        elif change_pct < -10:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'current_avg': round(recent_avg, 4),
            'previous_avg': round(earlier_avg, 4),
            'data_points': data_points
        }
    
    def analyze_participation_trend(self) -> Dict:
        """
        Analyze how participation balance changes over time
        
        Returns:
            {
                'trend': 'improving' | 'declining' | 'stable',
                'change_percentage': float,
                'current_balance': float,
                'previous_balance': float,
                'data_points': [{'date': str, 'balance': float}]
            }
        """
        if len(self.meetings) < 2:
            return {
                'trend': 'insufficient_data',
                'change_percentage': 0.0,
                'current_balance': 0.0,
                'previous_balance': 0.0,
                'data_points': []
            }
        
        data_points = [
            {
                'date': meeting.date.strftime('%Y-%m-%d'),
                'balance': meeting.participation_balance or 0.0
            }
            for meeting in self.meetings
        ]
        
        mid_point = len(self.meetings) // 2
        earlier_meetings = self.meetings[:mid_point]
        recent_meetings = self.meetings[mid_point:]
        
        earlier_balance = statistics.mean([m.participation_balance or 0.0 for m in earlier_meetings])
        recent_balance = statistics.mean([m.participation_balance or 0.0 for m in recent_meetings])
        
        change_pct = ((recent_balance - earlier_balance) / (earlier_balance + 0.001)) * 100
        
        if change_pct > 5:
            trend = 'improving'
        elif change_pct < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'current_balance': round(recent_balance, 4),
            'previous_balance': round(earlier_balance, 4),
            'data_points': data_points
        }
    
    def analyze_engagement_trend(self) -> Dict:
        """
        Analyze overall team engagement over time
        
        Returns:
            {
                'trend': 'improving' | 'declining' | 'stable',
                'change_percentage': float,
                'current_avg': float,
                'previous_avg': float,
                'data_points': [{'date': str, 'engagement': float}]
            }
        """
        if len(self.meetings) < 2:
            return {
                'trend': 'insufficient_data',
                'change_percentage': 0.0,
                'current_avg': 0.0,
                'previous_avg': 0.0,
                'data_points': []
            }
        
        data_points = []
        
        for meeting in self.meetings:
            avg_engagement = meeting.metrics.aggregate(Avg('engagement_score'))['engagement_score__avg'] or 0.0
            data_points.append({
                'date': meeting.date.strftime('%Y-%m-%d'),
                'engagement': round(avg_engagement, 2)
            })
        
        mid_point = len(data_points) // 2
        earlier_avg = statistics.mean([dp['engagement'] for dp in data_points[:mid_point]])
        recent_avg = statistics.mean([dp['engagement'] for dp in data_points[mid_point:]])
        
        change_pct = ((recent_avg - earlier_avg) / (earlier_avg + 0.001)) * 100
        
        if change_pct > 10:
            trend = 'improving'
        elif change_pct < -10:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'current_avg': round(recent_avg, 2),
            'previous_avg': round(earlier_avg, 2),
            'data_points': data_points
        }
    
    def analyze_message_volume_trend(self) -> Dict:
        """
        Analyze if team is becoming more or less communicative
        """
        if len(self.meetings) < 2:
            return {
                'trend': 'insufficient_data',
                'change_percentage': 0.0,
                'data_points': []
            }
        
        data_points = [
            {
                'date': meeting.date.strftime('%Y-%m-%d'),
                'messages': meeting.total_messages
            }
            for meeting in self.meetings
        ]
        
        mid_point = len(self.meetings) // 2
        earlier_avg = statistics.mean([m.total_messages for m in self.meetings[:mid_point]])
        recent_avg = statistics.mean([m.total_messages for m in self.meetings[mid_point:]])
        
        change_pct = ((recent_avg - earlier_avg) / (earlier_avg + 0.001)) * 100
        
        if change_pct > 15:
            trend = 'increasing'
        elif change_pct < -15:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'current_avg': round(recent_avg, 1),
            'previous_avg': round(earlier_avg, 1),
            'data_points': data_points
        }
    
    def get_comprehensive_analysis(self) -> Dict:
        """
        Get all trends in one call
        """
        return {
            'sentiment': self.analyze_sentiment_trend(),
            'participation': self.analyze_participation_trend(),
            'engagement': self.analyze_engagement_trend(),
            'message_volume': self.analyze_message_volume_trend(),
            'meeting_count': len(self.meetings)
        }


class SpeakerTrendAnalyzer:
    """
    Analyze trends for individual speakers across meetings
    """
    
    def __init__(self, speaker, meetings: List[Meeting]):
        self.speaker = speaker
        self.meetings = sorted(meetings, key=lambda m: m.date)
    
    def analyze_speaker_engagement_trend(self) -> Dict:
        """
        Track if a specific speaker is becoming more/less engaged
        """
        metrics = []
        
        for meeting in self.meetings:
            speaker_metric = meeting.metrics.filter(speaker=self.speaker).first()
            if speaker_metric:
                metrics.append({
                    'date': meeting.date.strftime('%Y-%m-%d'),
                    'engagement': speaker_metric.engagement_score,
                    'participation': speaker_metric.participation_percentage,
                    'sentiment': speaker_metric.avg_sentiment or 0.0
                })
        
        if len(metrics) < 2:
            return {
                'trend': 'insufficient_data',
                'data_points': metrics
            }
        
        # Compare recent vs earlier
        mid = len(metrics) // 2
        earlier_engagement = statistics.mean([m['engagement'] for m in metrics[:mid]])
        recent_engagement = statistics.mean([m['engagement'] for m in metrics[mid:]])
        
        change_pct = ((recent_engagement - earlier_engagement) / (earlier_engagement + 0.001)) * 100
        
        if change_pct > 15:
            trend = 'improving'
        elif change_pct < -15:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percentage': round(change_pct, 2),
            'data_points': metrics
        }
    