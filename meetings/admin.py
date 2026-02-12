from django.contrib import admin
from .models import Meeting, Speaker, Message, MeetingMetrics


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'total_messages', 'avg_sentiment', 'sentiment_label']
    list_filter = ['sentiment_label', 'date']
    search_fields = ['title']
    readonly_fields = ['total_messages', 'total_words', 'avg_sentiment', 'participation_balance']


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['speaker', 'meeting', 'word_count', 'sentiment_score', 'sequence_order']
    list_filter = ['meeting', 'speaker', 'is_question']
    search_fields = ['content']
    readonly_fields = ['word_count', 'sentiment_score']


@admin.register(MeetingMetrics)
class MeetingMetricsAdmin(admin.ModelAdmin):
    list_display = ['speaker', 'meeting', 'participation_percentage', 'engagement_score', 'avg_sentiment']
    list_filter = ['meeting']
    readonly_fields = ['total_messages', 'total_words', 'participation_percentage']
    