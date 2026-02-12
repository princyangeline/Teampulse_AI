from django import forms
from django.core.exceptions import ValidationError
import docx
import io


class TranscriptUploadForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Weekly Team Sync - Jan 2025'
        }),
        label='Meeting Title'
    )
    
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Date & Time'
    )
    
    duration_minutes = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '60'
        }),
        label='Duration (minutes)'
    )
    
    transcript_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.txt,.docx'
        }),
        label='Upload Transcript File',
        help_text='Supported formats: .txt, .docx'
    )
    
    transcript_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': 'Paste your meeting transcript here...\n\nExample formats:\nJohn: Hello everyone\nSarah: Hi John!\n\nOR\n\n[10:30] John: Hello everyone'
        }),
        label='Or Paste Transcript'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        transcript_file = self.files.get('transcript_file')  # Get file from request.FILES
        transcript_text = cleaned_data.get('transcript_text', '').strip()
        
        # Must have either file OR text
        if not transcript_file and not transcript_text:
            raise ValidationError('Please either upload a file or paste transcript text')
        
        # If file is uploaded, extract its content
        if transcript_file:
            file_name = transcript_file.name.lower()
            
            try:
                # Handle Word documents (.docx)
                if file_name.endswith('.docx'):
                    # Read file content
                    file_bytes = transcript_file.read()
                    
                    # Reset file pointer for potential reuse
                    transcript_file.seek(0)
                    
                    # Parse Word document
                    doc = docx.Document(io.BytesIO(file_bytes))
                    
                    # Extract all paragraphs
                    file_content = '\n'.join([
                        paragraph.text 
                        for paragraph in doc.paragraphs 
                        if paragraph.text.strip()
                    ])
                    
                    if not file_content.strip():
                        raise ValidationError('Word document appears to be empty')
                    
                    # Override transcript_text with file content
                    cleaned_data['transcript_text'] = file_content
                
                # Handle text files (.txt)
                elif file_name.endswith('.txt'):
                    # Read file content
                    file_bytes = transcript_file.read()
                    
                    # Reset file pointer for potential reuse
                    transcript_file.seek(0)
                    
                    # Decode to text
                    file_content = file_bytes.decode('utf-8')
                    
                    if not file_content.strip():
                        raise ValidationError('Text file appears to be empty')
                    
                    # Override transcript_text with file content
                    cleaned_data['transcript_text'] = file_content
                
                else:
                    raise ValidationError('Unsupported file format. Please upload .txt or .docx files only.')
                    
            except docx.oxml.exceptions.OxmlException:
                raise ValidationError('Invalid Word document. Please ensure the file is not corrupted.')
            except UnicodeDecodeError:
                raise ValidationError('Text file must be UTF-8 encoded')
            except ValidationError:
                raise  # Re-raise validation errors
            except Exception as e:
                raise ValidationError(f'Error reading file: {str(e)}')
        
        # Final validation: ensure we have transcript content
        final_transcript = cleaned_data.get('transcript_text', '').strip()
        if not final_transcript:
            raise ValidationError('Transcript content cannot be empty')
        
        return cleaned_data
    