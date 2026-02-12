from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List
from .parsers import TranscriptParser
import statistics
import re


class SentimentAnalyzer:
    """Analyze sentiment of messages"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Returns:
            {
                'compound': float,  # -1 to 1
                'positive': float,  # 0 to 1
                'negative': float,  # 0 to 1
                'neutral': float    # 0 to 1
            }
        """
        scores = self.analyzer.polarity_scores(text)
        return scores
    
    @staticmethod
    def get_label(compound_score: float) -> str:
        """Convert compound score to label"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'


class MessageAnalyzer:
    """Analyze individual messages"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_message(self, content: str) -> Dict:
        """
        Analyze a single message
        
        Returns:
            {
                'word_count': int,
                'sentiment_score': float,
                'sentiment_compound': float,
                'is_question': bool
            }
        """
        # FIXED: Proper word count calculation
        # Remove extra whitespace and split by spaces
        cleaned_content = ' '.join(content.split())
        
        # Count actual words (non-empty strings after splitting)
        words = [word for word in cleaned_content.split() if word.strip()]
        word_count = len(words)
        
        # Sentiment
        sentiment = self.sentiment_analyzer.analyze(content)
        
        # Question detection
        is_question = '?' in content or any(
            content.lower().strip().startswith(q) 
            for q in ['who', 'what', 'where', 'when', 'why', 'how', 'is', 'are', 'can', 'could', 'would', 'should', 'do', 'does', 'did']
        )
        
        return {
            'word_count': word_count,
            'sentiment_score': sentiment['compound'],
            'sentiment_compound': sentiment['compound'],
            'is_question': is_question
        }


class MeetingAnalyzer:
    """
    Analyze meeting-level metrics
    """
    
    def __init__(self, meeting, parsed_messages):
        """
        Initialize analyzer
        
        Args:
            meeting: Meeting model instance
            parsed_messages: List of dictionaries with message data
        """
        self.meeting = meeting
        self.parsed_messages = parsed_messages
    
    def analyze_and_save(self):
        """
        Analyze messages and save to database
        """
        from .models import Speaker, Message, MeetingMetrics
        
        message_analyzer = MessageAnalyzer()
        
        # Process each message
        for msg_data in self.parsed_messages:
            # Get or create speaker
            speaker_name = TranscriptParser.clean_speaker_name(msg_data['speaker'])
            speaker, _ = Speaker.objects.get_or_create(name=speaker_name)
            
            # Analyze message content
            analysis = message_analyzer.analyze_message(msg_data['content'])
            
            # Create message record
            Message.objects.create(
                meeting=self.meeting,
                speaker=speaker,
                content=msg_data['content'],
                timestamp=msg_data.get('timestamp'),
                sequence_order=msg_data['sequence'],
                word_count=analysis['word_count'],
                sentiment_score=analysis['sentiment_score'],
                sentiment_compound=analysis['sentiment_compound'],
                is_question=analysis['is_question']
            )
        
        # Calculate speaker metrics
        self._calculate_speaker_metrics()
        
        # Calculate meeting aggregates
        self._calculate_meeting_aggregates()
    
    def _calculate_speaker_metrics(self):
        """Calculate metrics for each speaker"""
        from .models import Speaker, MeetingMetrics
        
        # Get all speakers in this meeting
        speakers = Speaker.objects.filter(
            messages__meeting=self.meeting
        ).distinct()
        
        total_messages = self.meeting.messages.count()
        total_words = sum(msg.word_count for msg in self.meeting.messages.all())
        
        for speaker in speakers:
            speaker_messages = self.meeting.messages.filter(speaker=speaker)
            
            # Calculate metrics
            speaker_message_count = speaker_messages.count()
            speaker_word_count = sum(msg.word_count for msg in speaker_messages)
            
            participation_pct = (speaker_message_count / total_messages * 100) if total_messages > 0 else 0
            avg_words = speaker_word_count / speaker_message_count if speaker_message_count > 0 else 0
            
            # Sentiment metrics
            sentiments = [msg.sentiment_score for msg in speaker_messages if msg.sentiment_score is not None]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Count sentiment categories
            positive_count = sum(1 for s in sentiments if s > 0.05)
            negative_count = sum(1 for s in sentiments if s < -0.05)
            neutral_count = len(sentiments) - positive_count - negative_count
            
            # Question count
            question_count = speaker_messages.filter(is_question=True).count()
            
            # Engagement score (composite metric)
            engagement_score = self._calculate_engagement_score(
                avg_words, question_count, speaker_message_count, participation_pct
            )
            
            # Save metrics
            MeetingMetrics.objects.create(
                meeting=self.meeting,
                speaker=speaker,
                total_messages=speaker_message_count,
                total_words=speaker_word_count,
                participation_percentage=participation_pct,
                avg_words_per_message=avg_words,
                avg_sentiment=avg_sentiment,
                positive_count=positive_count,
                neutral_count=neutral_count,
                negative_count=negative_count,
                question_count=question_count,
                engagement_score=engagement_score
            )
    
    def _calculate_engagement_score(self, avg_words, questions, messages, participation):
        """
        Calculate engagement score (0-100)
        
        Factors:
        - Average message length (longer = more engaged)
        - Question count (questions show engagement)
        - Message frequency relative to participation
        """
        # Normalize components
        word_score = min(avg_words / 20 * 100, 100)  # 20 words = 100%
        question_score = min(questions / messages * 100, 100) if messages > 0 else 0
        participation_score = min(participation, 100)
        
        # Weighted average
        engagement = (
            word_score * 0.4 +
            question_score * 0.3 +
            participation_score * 0.3
        )
        
        return round(engagement, 2)
    
    def _calculate_meeting_aggregates(self):
        """Calculate meeting-level aggregate metrics"""
        messages = self.meeting.messages.all()
        
        # Average sentiment
        sentiments = [msg.sentiment_score for msg in messages if msg.sentiment_score is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Sentiment label
        if avg_sentiment > 0.1:
            sentiment_label = 'positive'
        elif avg_sentiment < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        # Participation balance (Gini coefficient)
        participation_balance = self._calculate_participation_balance()
        
        # Total counts
        total_messages = messages.count()
        total_words = sum(msg.word_count for msg in messages)
        
        # Update meeting
        self.meeting.avg_sentiment = avg_sentiment
        self.meeting.sentiment_label = sentiment_label
        self.meeting.participation_balance = participation_balance
        self.meeting.total_messages = total_messages
        self.meeting.total_words = total_words
        self.meeting.save()
    
    def _calculate_participation_balance(self):
        """
        Calculate Gini coefficient for participation balance
        0 = perfectly imbalanced (one person talks)
        1 = perfectly balanced (everyone talks equally)
        """
        metrics = list(self.meeting.metrics.all())
        
        if len(metrics) <= 1:
            return 1.0
        
        # Get participation percentages
        participations = [m.participation_percentage for m in metrics]
        participations.sort()
        
        n = len(participations)
        cumsum = 0
        
        for i, p in enumerate(participations):
            cumsum += (n - i) * p
        
        gini = (2 * cumsum) / (n * sum(participations)) - (n + 1) / n
        balance = 1 - gini
        
        return max(0, min(1, balance))  # Clamp between 0 and 1
    
    
