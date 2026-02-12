from typing import Dict, List
from .models import Meeting
from .trend_analyzer import TrendAnalyzer
import statistics


def calculate_team_health_index(meetings: List[Meeting]) -> Dict:
    """
    Calculate comprehensive Team Health Index (0-100)
    
    Components:
    - Sentiment trend (30%)
    - Participation balance (30%)
    - Engagement trend (20%)
    - Communication volume (20%)
    """
    if len(meetings) < 2:
        return {
            'score': 0,
            'level': 'unknown',
            'color': 'secondary',
            'icon': '❓',
            'components': {}
        }
    
    trend_analyzer = TrendAnalyzer(meetings)
    
    # Get trends
    sentiment = trend_analyzer.analyze_sentiment_trend()
    participation = trend_analyzer.analyze_participation_trend()
    engagement = trend_analyzer.analyze_engagement_trend()
    volume = trend_analyzer.analyze_message_volume_trend()
    
    # Calculate component scores (0-100)
    
    # Sentiment score (higher sentiment = higher score)
    sentiment_score = (sentiment['current_avg'] + 1) * 50  # Convert -1 to 1 range to 0-100
    
    # Participation score (higher balance = higher score)
    participation_score = participation['current_balance'] * 100
    
    # Engagement score (directly use engagement)
    engagement_score = engagement['current_avg']
    
    # Volume score (stable is good, too high/low is bad)
    if volume['trend'] == 'stable':
        volume_score = 80
    elif volume['trend'] == 'increasing':
        volume_score = 70  # Might be good, might be chaotic
    else:
        volume_score = 50  # Declining could indicate disengagement
    
    # Weighted average
    health_score = (
        sentiment_score * 0.30 +
        participation_score * 0.30 +
        engagement_score * 0.20 +
        volume_score * 0.20
    )
    
    # Determine health level
    if health_score >= 80:
        level = 'excellent'
        color = 'success'
        icon = '🌟'
    elif health_score >= 65:
        level = 'good'
        color = 'info'
        icon = '✅'
    elif health_score >= 50:
        level = 'fair'
        color = 'warning'
        icon = '⚠️'
    else:
        level = 'poor'
        color = 'danger'
        icon = '🚨'
    
    return {
        'score': round(health_score, 1),
        'level': level,
        'color': color,
        'icon': icon,
        'components': {
            'sentiment': {
                'score': round(sentiment_score, 1),
                'trend': sentiment['trend'],
                'current': sentiment['current_avg']
            },
            'participation': {
                'score': round(participation_score, 1),
                'trend': participation['trend'],
                'current': participation['current_balance']
            },
            'engagement': {
                'score': round(engagement_score, 1),
                'trend': engagement['trend'],
                'current': engagement['current_avg']
            },
            'volume': {
                'score': round(volume_score, 1),
                'trend': volume['trend']
            }
        }
    }
