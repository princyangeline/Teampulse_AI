from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Meeting(models.Model):
    """Represents a single meeting session"""
    title = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    raw_transcript = models.TextField(help_text="Original transcript text")
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Aggregate metrics (computed after analysis)
    total_messages = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)
    avg_sentiment = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(
        max_length=20, 
        choices=[
            ('positive', 'Positive'),
            ('neutral', 'Neutral'),
            ('negative', 'Negative')
        ],
        null=True,
        blank=True
    )
    participation_balance = models.FloatField(
        null=True, 
        blank=True,
        help_text="0-1 score where 1 is perfectly balanced"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"


class Speaker(models.Model):
    """Represents a participant in meetings"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Message(models.Model):
    """Individual message/utterance in a meeting"""
    meeting = models.ForeignKey(
        Meeting, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    speaker = models.ForeignKey(
        Speaker, 
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content = models.TextField()
    timestamp = models.CharField(max_length=20, null=True, blank=True)
    sequence_order = models.IntegerField(help_text="Order in the meeting")
    
    # Analysis fields
    word_count = models.IntegerField(default=0)
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Sentiment from -1 (negative) to 1 (positive)"
    )
    sentiment_compound = models.FloatField(null=True, blank=True)
    is_question = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['meeting', 'sequence_order']
    
    def __str__(self):
        return f"{self.speaker.name}: {self.content[:50]}..."


class MeetingMetrics(models.Model):
    """Per-speaker metrics for a specific meeting"""
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # Participation metrics
    total_messages = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)
    participation_percentage = models.FloatField(default=0.0)
    avg_words_per_message = models.FloatField(default=0.0)
    
    # Engagement metrics
    engagement_score = models.FloatField(
        default=0.0,
        help_text="Composite score of involvement (0-100)"
    )
    
    # Sentiment metrics
    avg_sentiment = models.FloatField(null=True, blank=True)
    positive_count = models.IntegerField(default=0)  # FIXED: changed from positive_message_count
    negative_count = models.IntegerField(default=0)  # FIXED: changed from negative_message_count
    neutral_count = models.IntegerField(default=0)   # FIXED: changed from neutral_message_count
    
    # Behavioral metrics
    question_count = models.IntegerField(default=0)
    interruption_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['meeting', 'speaker']
        ordering = ['-participation_percentage']
    
    def __str__(self):
        return f"{self.speaker.name} in {self.meeting.title}"
    