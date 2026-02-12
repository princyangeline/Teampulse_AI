from typing import Dict, List
from .models import Meeting, MeetingMetrics
from .trend_analyzer import TrendAnalyzer
from .risk_detector import RiskDetector
import statistics


class TeamInsightsGenerator:
    """
    Generate natural language insights and recommendations for team health
    """
    
    def __init__(self, meetings: List[Meeting]):
        self.meetings = sorted(meetings, key=lambda m: m.date)
        self.trend_analyzer = TrendAnalyzer(meetings) if len(meetings) >= 2 else None
        self.risk_detector = RiskDetector(meetings) if len(meetings) >= 2 else None
    
    def generate_executive_summary(self) -> str:
        """
        Generate a natural language executive summary of team health
        """
        if not self.meetings:
            return "No meeting data available for analysis."
        
        if len(self.meetings) < 2:
            meeting = self.meetings[0]
            return self._generate_single_meeting_summary(meeting)
        
        # Multi-meeting analysis
        trends = self.trend_analyzer.get_comprehensive_analysis()
        
        summary_parts = []
        
        # Sentiment observation
        sentiment = trends['sentiment']
        if sentiment['trend'] == 'improving':
            summary_parts.append(f"Team morale is improving, with sentiment rising {abs(sentiment['change_percentage']):.1f}% over recent meetings")
        elif sentiment['trend'] == 'declining':
            summary_parts.append(f"Team morale has declined {abs(sentiment['change_percentage']):.1f}%, indicating possible frustration or disagreement")
        else:
            summary_parts.append("Team sentiment remains stable")
        
        # Participation observation
        participation = trends['participation']
        if participation['trend'] == 'declining':
            summary_parts.append(f"participation balance has decreased {abs(participation['change_percentage']):.1f}%, suggesting rising dominance patterns")
        elif participation['trend'] == 'improving':
            summary_parts.append(f"participation is becoming more balanced across the team")
        
        # Engagement observation
        engagement = trends['engagement']
        if engagement['trend'] == 'declining':
            summary_parts.append(f"Team engagement has dropped {abs(engagement['change_percentage']):.1f}%, which may indicate fatigue or disinterest")
        elif engagement['trend'] == 'improving':
            summary_parts.append(f"team members are becoming more actively engaged")
        
        # Combine into coherent summary
        if len(summary_parts) >= 2:
            summary = f"{summary_parts[0]}, but {summary_parts[1]}"
            if len(summary_parts) >= 3:
                summary += f". Additionally, {summary_parts[2]}"
        else:
            summary = ". ".join(summary_parts)
        
        return summary.capitalize() + "."
    
    def _generate_single_meeting_summary(self, meeting: Meeting) -> str:
        """Generate summary for a single meeting"""
        parts = []
        
        if meeting.avg_sentiment > 0.3:
            parts.append("The meeting had a positive and constructive tone")
        elif meeting.avg_sentiment < -0.1:
            parts.append("The meeting showed signs of tension or disagreement")
        else:
            parts.append("The meeting maintained a neutral, professional tone")
        
        if meeting.participation_balance > 0.7:
            parts.append("with well-balanced participation across team members")
        elif meeting.participation_balance < 0.4:
            parts.append("though a few individuals dominated most of the conversation")
        
        return ". ".join(parts) + "."
    
    def identify_key_strengths(self) -> List[str]:
        """
        Identify positive patterns in team collaboration
        """
        if len(self.meetings) < 2:
            return self._single_meeting_strengths()
        
        trends = self.trend_analyzer.get_comprehensive_analysis()
        strengths = []
        
        # Check sentiment
        if trends['sentiment']['current_avg'] > 0.2:
            strengths.append("Team maintains positive and constructive communication")
        
        # Check participation
        if trends['participation']['current_balance'] > 0.65:
            strengths.append("Participation is well-distributed across team members")
        
        # Check engagement
        if trends['engagement']['current_avg'] > 65:
            strengths.append("Team members demonstrate strong active engagement")
        
        # Check improvement trends
        if trends['sentiment']['trend'] == 'improving':
            strengths.append("Team morale is trending upward")
        
        if trends['engagement']['trend'] == 'improving':
            strengths.append("Team engagement is increasing over time")
        
        if not strengths:
            strengths.append("Team maintains consistent meeting attendance and participation")
        
        return strengths[:3]  # Top 3
    
    def _single_meeting_strengths(self) -> List[str]:
        """Strengths from single meeting"""
        meeting = self.meetings[0]
        strengths = []
        
        if meeting.avg_sentiment > 0.2:
            strengths.append("Positive and constructive dialogue throughout the meeting")
        
        if meeting.participation_balance > 0.6:
            strengths.append("Balanced participation across team members")
        
        metrics = meeting.metrics.all()
        question_ratio = sum(m.question_count for m in metrics) / max(meeting.total_messages, 1)
        if question_ratio > 0.15:
            strengths.append("High level of inquiry and active problem-solving")
        
        return strengths if strengths else ["Team completed the meeting as scheduled"]
    
    def identify_primary_risks(self) -> List[Dict]:
        """
        Identify top risks with explanations
        """
        if len(self.meetings) < 2:
            return []
        
        risks = self.risk_detector.get_comprehensive_risk_analysis()
        risk_items = []
        
        # Conflict risk
        if risks['conflict_risk']['risk_level'] in ['high', 'medium']:
            risk_items.append({
                'type': 'Conflict Risk',
                'level': risks['conflict_risk']['risk_level'],
                'score': risks['conflict_risk']['risk_score'],
                'explanation': ' '.join(risks['conflict_risk']['indicators'][:2]),
                'impact': 'May lead to decreased collaboration and team cohesion'
            })
        
        # Burnout risk
        if risks['burnout_risk']['risk_level'] in ['high', 'medium']:
            risk_items.append({
                'type': 'Burnout Risk',
                'level': risks['burnout_risk']['risk_level'],
                'score': risks['burnout_risk']['risk_score'],
                'explanation': ' '.join(risks['burnout_risk']['indicators'][:2]),
                'impact': 'Could result in reduced productivity and team turnover'
            })
        
        # Dominance issues
        if risks['dominance_issues']['risk_level'] in ['high', 'medium']:
            dominant = ', '.join(risks['dominance_issues']['dominant_speakers'][:2])
            risk_items.append({
                'type': 'Conversation Dominance',
                'level': risks['dominance_issues']['risk_level'],
                'score': risks['dominance_issues']['risk_score'],
                'explanation': f"Conversation dominated by {dominant}",
                'impact': 'Quieter team members may feel unheard or disengaged'
            })
        
        # Disengagement
        if risks['disengagement_risk']['risk_level'] in ['high', 'medium']:
            at_risk = risks['disengagement_risk'].get('at_risk_speakers', [])
            if at_risk:
                names = ', '.join([s['name'] for s in at_risk[:2]])
                risk_items.append({
                    'type': 'Team Disengagement',
                    'level': risks['disengagement_risk']['risk_level'],
                    'score': 50,  # Default score
                    'explanation': f"{names} showing declining engagement patterns",
                    'impact': 'May indicate burnout or role dissatisfaction'
                })
        
        # Sort by score and return top 3
        risk_items.sort(key=lambda x: x['score'], reverse=True)
        return risk_items[:3]
    
    def generate_recommended_actions(self) -> List[Dict]:
        """
        Generate specific, actionable recommendations
        """
        if len(self.meetings) < 2:
            return self._single_meeting_actions()
        
        risks = self.risk_detector.get_comprehensive_risk_analysis()
        trends = self.trend_analyzer.get_comprehensive_analysis()
        actions = []
        
        # Sentiment-based actions
        if trends['sentiment']['trend'] == 'declining':
            actions.append({
                'priority': 'High',
                'action': 'Schedule a team retrospective',
                'reason': f"Sentiment has declined {abs(trends['sentiment']['change_percentage']):.1f}% over recent meetings",
                'expected_impact': 'Surface and address team concerns before they escalate'
            })
        
        # Participation-based actions
        if trends['participation']['trend'] == 'declining':
            actions.append({
                'priority': 'High',
                'action': 'Implement round-robin speaking format',
                'reason': 'Participation balance is decreasing, suggesting emerging dominance patterns',
                'expected_impact': 'Ensure all voices are heard and valued'
            })
        
        # Dominance-based actions
        if risks['dominance_issues']['risk_level'] in ['high', 'medium']:
            dominant = risks['dominance_issues']['dominant_speakers']
            if dominant:
                actions.append({
                    'priority': 'Medium',
                    'action': f'Explicitly invite input from quieter team members',
                    'reason': f"{dominant[0]} dominates {risks['dominance_issues']['risk_score']}% of discussion time",
                    'expected_impact': 'Build psychological safety and inclusive culture'
                })
        
        # Engagement-based actions
        if trends['engagement']['trend'] == 'declining':
            actions.append({
                'priority': 'High',
                'action': 'Conduct 1-on-1 check-ins with team members',
                'reason': f"Team engagement has dropped {abs(trends['engagement']['change_percentage']):.1f}%",
                'expected_impact': 'Identify and address individual concerns or blockers'
            })
        
        # Burnout-based actions
        if risks['burnout_risk']['risk_level'] == 'high':
            actions.append({
                'priority': 'Critical',
                'action': 'Review workload distribution and meeting frequency',
                'reason': 'Multiple burnout indicators detected across the team',
                'expected_impact': 'Prevent team burnout and maintain sustainable pace'
            })
        
        # Disengagement-based actions
        at_risk = risks['disengagement_risk'].get('at_risk_speakers', [])
        if at_risk:
            names = ', '.join([s['name'] for s in at_risk[:2]])
            actions.append({
                'priority': 'High',
                'action': f'Meet individually with {names}',
                'reason': 'These members show declining engagement patterns',
                'expected_impact': 'Re-engage team members and address potential issues'
            })
        
        # Sort by priority
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        actions.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return actions[:4]  # Top 4 actions
    
    def _single_meeting_actions(self) -> List[Dict]:
        """Actions from single meeting"""
        meeting = self.meetings[0]
        actions = []
        
        if meeting.participation_balance < 0.5:
            actions.append({
                'priority': 'Medium',
                'action': 'Implement structured turn-taking in next meeting',
                'reason': 'Participation was imbalanced in this meeting',
                'expected_impact': 'Ensure all team members contribute equally'
            })
        
        if meeting.avg_sentiment < 0:
            actions.append({
                'priority': 'High',
                'action': 'Follow up on topics that generated tension',
                'reason': 'Meeting showed negative sentiment',
                'expected_impact': 'Resolve disagreements before they grow'
            })
        
        return actions
    
    def get_top_priorities(self) -> List[Dict]:
        """
        Get top 3 most urgent team priorities
        """
        if len(self.meetings) < 2:
            return []
        
        risks = self.risk_detector.get_comprehensive_risk_analysis()
        trends = self.trend_analyzer.get_comprehensive_analysis()
        
        priorities = []
        
        # Critical: Burnout
        if risks['burnout_risk']['risk_level'] == 'high':
            priorities.append({
                'rank': 1,
                'title': 'Address Team Burnout Signals',
                'severity': 'Critical',
                'description': 'Multiple indicators suggest team fatigue. Engagement down, communication decreasing.',
                'action': 'Review workload and reduce meeting frequency'
            })
        
        # High: Conflict
        if risks['conflict_risk']['risk_level'] in ['high', 'medium']:
            priorities.append({
                'rank': len(priorities) + 1,
                'title': 'Resolve Rising Team Tensions',
                'severity': 'High',
                'description': f"Sentiment declined {abs(trends['sentiment']['change_percentage']):.1f}% with increasing negative interactions",
                'action': 'Schedule team retrospective to surface concerns'
            })
        
        # High: Dominance
        if risks['dominance_issues']['risk_level'] == 'high':
            dominant = risks['dominance_issues']['dominant_speakers']
            if dominant:
                priorities.append({
                    'rank': len(priorities) + 1,
                    'title': 'Rebalance Meeting Participation',
                    'severity': 'High',
                    'description': f"{dominant[0]} controls {risks['dominance_issues']['risk_score']}% of discussion",
                    'action': 'Use round-robin format to ensure all voices heard'
                })
        
        # Medium: Declining engagement
        if trends['engagement']['trend'] == 'declining' and trends['engagement']['change_percentage'] < -15:
            priorities.append({
                'rank': len(priorities) + 1,
                'title': 'Boost Team Engagement',
                'severity': 'Medium',
                'description': f"Engagement dropped {abs(trends['engagement']['change_percentage']):.1f}% over recent meetings",
                'action': 'Conduct 1-on-1s to identify blockers'
            })
        
        return priorities[:3]
    
    def generate_ai_insight_banner(self) -> Dict:
        if len(self.meetings) < 2:
            meeting = self.meetings[0]
            return {
                'main_message': f"First meeting analyzed. Team showed {meeting.sentiment_label} sentiment with {meeting.total_messages} exchanges. Baseline established for future trend detection.",
                'primary_concern': None,
                'recommended_focus': "Continue monitoring participation balance and engagement patterns."
            }
        
        trends = self.trend_analyzer.get_comprehensive_analysis()
        risks = self.risk_detector.get_comprehensive_risk_analysis()
        
        # Determine the most critical insight
        main_message = self._generate_main_narrative(trends, risks)
        primary_concern = self._identify_primary_concern(trends, risks)
        recommended_focus = self._generate_recommended_focus(trends, risks)
        
        return {
            'main_message': main_message,
            'primary_concern': primary_concern,
            'recommended_focus': recommended_focus
        }

    def _generate_main_narrative(self, trends, risks) -> str:
        """Generate the main AI narrative"""
        sentiment_trend = trends['sentiment']['trend']
        engagement_trend = trends['engagement']['trend']
        participation_trend = trends['participation']['trend']
        
        # Critical scenario: Multiple declining metrics
        if (sentiment_trend == 'declining' and engagement_trend == 'declining'):
            return f"Your team is showing early warning signs of collaborative fatigue. While {abs(trends['sentiment']['change_percentage']):.1f}% sentiment decline could indicate frustration with processes or decisions, the {abs(trends['engagement']['change_percentage']):.1f}% drop in engagement suggests team members may be withdrawing from active participation."
        
        # Positive scenario: Improving trends
        if sentiment_trend == 'improving' and engagement_trend == 'improving':
            return f"Team collaboration is strengthening. Sentiment has improved {abs(trends['sentiment']['change_percentage']):.1f}% and engagement is up {abs(trends['engagement']['change_percentage']):.1f}%, indicating team members feel more positive and are participating more actively in discussions."
        
        # Mixed scenario: Sentiment up but engagement down
        if sentiment_trend == 'improving' and engagement_trend == 'declining':
            return f"Your team shows a complex pattern: morale is improving ({abs(trends['sentiment']['change_percentage']):.1f}% increase) but active engagement has dropped {abs(trends['engagement']['change_percentage']):.1f}%. This often signals that while the team feels better about outcomes, some members may be experiencing fatigue or reduced ownership."
        
        # Mixed scenario: Engagement up but sentiment down
        if sentiment_trend == 'declining' and engagement_trend == 'improving':
            return f"Team members are engaging more actively ({abs(trends['engagement']['change_percentage']):.1f}% increase), but sentiment has declined {abs(trends['sentiment']['change_percentage']):.1f}%. This pattern often indicates passionate disagreement or frustration with project direction—high energy but growing tension."
        
        # Participation imbalance
        if participation_trend == 'declining' and trends['participation']['current_balance'] < 0.5:
            return f"Conversation dynamics are becoming increasingly imbalanced. Participation equity has dropped {abs(trends['participation']['change_percentage']):.1f}%, suggesting a few voices are dominating while others are contributing less. This can lead to disengagement among quieter team members."
        
        # Stable but needs attention
        if sentiment_trend == 'stable' and trends['sentiment']['current_avg'] < 0:
            return f"Team sentiment has stabilized but remains in negative territory (score: {trends['sentiment']['current_avg']:.2f}). While there's no active decline, the persistent low morale suggests underlying issues that haven't been addressed."
        
        # Default positive stable
        return f"Team collaboration appears stable with consistent sentiment and engagement levels. Monitoring continues to detect any emerging patterns or shifts in team dynamics."

    def _identify_primary_concern(self, trends, risks) -> str:
        """Identify the single most critical concern"""
        # Check for critical risks first
        if risks['burnout_risk']['risk_level'] == 'high':
            return f"Burnout risk detected: {risks['burnout_risk']['indicators'][0]} This requires immediate leadership attention."
        
        if risks['conflict_risk']['risk_level'] == 'high':
            return f"Conflict indicators emerging: {risks['conflict_risk']['indicators'][0]} Consider facilitating team discussion."
        
        if risks['dominance_issues']['risk_level'] == 'high':
            dominant = risks['dominance_issues']['dominant_speakers']
            if dominant:
                return f"{dominant[0]} is dominating {risks['dominance_issues']['risk_score']:.0f}% of conversations, potentially silencing other voices."
        
        # Check for declining trends
        if trends['engagement']['trend'] == 'declining' and abs(trends['engagement']['change_percentage']) > 15:
            return f"Team engagement has dropped {abs(trends['engagement']['change_percentage']):.1f}% — investigate workload, clarity, and individual team member concerns."
        
        if trends['sentiment']['trend'] == 'declining' and abs(trends['sentiment']['change_percentage']) > 10:
            return f"Team morale declining {abs(trends['sentiment']['change_percentage']):.1f}% — recent decisions or processes may be creating frustration."
        
        # No critical concerns
        return None

    def _generate_recommended_focus(self, trends, risks) -> str:
        """Generate actionable leadership recommendation"""
        # Prioritize based on risk level
        if risks['burnout_risk']['risk_level'] in ['high', 'medium']:
            return "Schedule 1-on-1s with team members to understand workload, blockers, and energy levels. Consider reducing meeting frequency or scope."
        
        if risks['conflict_risk']['risk_level'] in ['high', 'medium']:
            return "Hold a team retrospective to surface tensions constructively. Create space for disagreement while building toward shared solutions."
        
        if risks['dominance_issues']['risk_level'] in ['high', 'medium']:
            return "Implement structured turn-taking in meetings (round-robin, explicit prompts for quiet members). Coach dominant speakers on active listening."
        
        # Engagement declining
        if trends['engagement']['trend'] == 'declining':
            return "Check in with individual contributors about clarity, autonomy, and whether they feel heard. Engagement drops often signal role confusion or lack of agency."
        
        # Sentiment declining
        if trends['sentiment']['trend'] == 'declining':
            return "Review recent decisions and process changes. Team frustration often stems from feeling excluded from decisions that affect their work."
        
        # Participation imbalance
        if trends['participation']['trend'] == 'declining':
            return "Create meeting norms that ensure balanced airtime. Ask quieter members direct questions and protect their speaking time from interruption."
        
        # Positive reinforcement
        if trends['sentiment']['trend'] == 'improving':
            return "Continue current collaboration practices. Team morale is improving—reinforce what's working through recognition and consistency."
        
        return "Maintain current team dynamics monitoring. No urgent interventions needed, but continue watching for emerging patterns."
