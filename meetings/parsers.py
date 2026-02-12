import re
from typing import List, Dict, Optional
from datetime import datetime


class TranscriptParser:
    """
    Parse meeting transcripts in various formats
    """
    
    def __init__(self, transcript_text: str):
        self.transcript_text = transcript_text
        self.messages = []
    
    def parse(self) -> List[Dict]:
        """
        Parse transcript and return structured data
        Returns list of message dictionaries
        """
        lines = self.transcript_text.strip().split('\n')
        
        # Detect format
        format_type = self._detect_format(lines)
        
        if format_type == 'colon':
            return self._parse_colon_format(lines)
        elif format_type == 'timestamp':
            return self._parse_timestamp_format(lines)
        else:
            # Fallback: try colon format
            return self._parse_colon_format(lines)
    
    def _detect_format(self, lines: List[str]) -> str:
        """Detect transcript format"""
        # Check first few non-empty lines
        sample_lines = [line for line in lines[:10] if line.strip()]
        
        # Timestamp format: [HH:MM] Speaker: Message
        timestamp_pattern = r'\[?\d{1,2}:\d{2}\]?\s+\w+:'
        
        # Colon format: Speaker: Message
        colon_pattern = r'^\w+.*?:\s+'
        
        timestamp_count = sum(1 for line in sample_lines if re.search(timestamp_pattern, line))
        colon_count = sum(1 for line in sample_lines if re.search(colon_pattern, line))
        
        if timestamp_count > len(sample_lines) / 2:
            return 'timestamp'
        elif colon_count > len(sample_lines) / 2:
            return 'colon'
        else:
            return 'colon'  # Default
    
    def _parse_colon_format(self, lines: List[str]) -> List[Dict]:
        """Parse colon-separated format (Speaker: Message)"""
        messages = []
        sequence = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match pattern: Speaker: Message
            match = re.match(r'^([^:]+):\s*(.+)$', line)
            
            if match:
                speaker = match.group(1).strip()
                content = match.group(2).strip()
                
                if speaker and content:
                    sequence += 1
                    messages.append({
                        'speaker': speaker,
                        'content': content,
                        'timestamp': None,
                        'sequence': sequence
                    })
        
        return messages
    
    def _parse_timestamp_format(self, lines: List[str]) -> List[Dict]:
        """Parse timestamp format ([HH:MM] Speaker: Message)"""
        messages = []
        sequence = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match pattern: [HH:MM] Speaker: Message or [HH:MM:SS] Speaker: Message
            match = re.match(r'\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+([^:]+):\s*(.+)$', line)
            
            if match:
                timestamp = match.group(1)
                speaker = match.group(2).strip()
                content = match.group(3).strip()
                
                if speaker and content:
                    sequence += 1
                    messages.append({
                        'speaker': speaker,
                        'content': content,
                        'timestamp': timestamp,
                        'sequence': sequence
                    })
        
        return messages
    
    @staticmethod
    def clean_speaker_name(speaker: str) -> str:
        """Clean and normalize speaker names"""
        # Remove extra whitespace
        speaker = speaker.strip()
        
        # Remove timestamps if accidentally included
        speaker = re.sub(r'\[?\d{1,2}:\d{2}(?::\d{2})?\]?', '', speaker)
        
        # Capitalize first letter of each word
        speaker = ' '.join(word.capitalize() for word in speaker.split())
        
        return speaker


class TranscriptValidator:
    """
    Validate transcript format and content
    """
    
    def __init__(self):
        self.errors = []
    
    def validate(self, transcript_text: str) -> bool:
        """
        Validate transcript content
        Returns True if valid, False otherwise
        """
        self.errors = []
        
        if not transcript_text or not transcript_text.strip():
            self.errors.append("Transcript is empty")
            return False
        
        # Check minimum length
        if len(transcript_text.strip()) < 20:
            self.errors.append("Transcript is too short (minimum 20 characters)")
            return False
        
        # Check for speaker patterns
        lines = transcript_text.strip().split('\n')
        valid_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for speaker pattern (name: content)
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    valid_lines += 1
        
        if valid_lines < 2:
            self.errors.append("Could not find valid speaker format. Expected format: 'Speaker: Message'")
            return False
        
        return True
    