# Whisper Speech-to-Text Integration Guidelines

## Overview
Configuration guidelines for integrating OpenAI Whisper speech-to-text capabilities in the ex-GPT system, specifically for meeting transcription, voice queries, and automated documentation workflows at Korea Expressway Corporation.

## Whisper Setup and Configuration

### Basic Installation and Setup
```python
import whisper
import torch
import numpy as np
from typing import Optional, Dict, List, Tuple
import asyncio
import tempfile
import os
from pathlib import Path
import librosa
from pydub import AudioSegment
import io

class WhisperManager:
    def __init__(self, 
                 model_size: str = "large-v3",
                 device: str = "cuda",
                 compute_type: str = "float16"):
        
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        
        # Load Whisper model with optimized settings
        self.model = whisper.load_model(
            model_size,
            device=device,
            in_memory=True  # Keep model in memory for faster inference
        )
        
        # Audio preprocessing settings
        self.sample_rate = 16000
        self.chunk_duration = 30  # seconds
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
        
        # Korean language optimization
        self.default_options = {
            "language": "ko",
            "task": "transcribe",
            "fp16": True if device == "cuda" else False,
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0.0,
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "condition_on_previous_text": True,
            "prompt_reset_on_temperature": 0.5,
            "suppress_tokens": [-1],
            "without_timestamps": False,
            "max_initial_timestamp": 1.0,
            "word_timestamps": True
        }
```

### Audio Processing and Optimization
```python
class AudioPreprocessor:
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
        
    def preprocess_audio(self, audio_path: str) -> np.ndarray:
        """Preprocess audio file for optimal Whisper performance"""
        
        # Load audio file
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Resample to target sample rate if needed
        if sr != self.target_sample_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sample_rate)
        
        # Normalize audio
        audio = librosa.util.normalize(audio)
        
        # Apply noise reduction (simple)
        audio = self._reduce_noise(audio)
        
        # Remove silence
        audio = self._remove_silence(audio)
        
        return audio
    
    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """Simple noise reduction using spectral gating"""
        # This is a simplified noise reduction
        # In production, consider using more sophisticated methods
        return audio
    
    def _remove_silence(self, audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Remove silent parts from audio"""
        # Find non-silent intervals
        intervals = librosa.effects.split(
            audio, 
            top_db=20,  # Silence threshold in dB
            frame_length=2048,
            hop_length=512
        )
        
        # Concatenate non-silent parts
        if len(intervals) > 0:
            non_silent_audio = np.concatenate([audio[start:end] for start, end in intervals])
            return non_silent_audio
        
        return audio
    
    def convert_to_wav(self, input_path: str, output_path: str = None) -> str:
        """Convert audio file to WAV format"""
        if output_path is None:
            output_path = input_path.rsplit('.', 1)[0] + '.wav'
        
        # Load and convert using pydub
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(self.target_sample_rate)
        audio = audio.set_channels(1)  # Convert to mono
        audio.export(output_path, format="wav")
        
        return output_path
```

### Meeting Transcription System
```python
class MeetingTranscriber:
    def __init__(self, whisper_manager: WhisperManager):
        self.whisper_manager = whisper_manager
        self.preprocessor = AudioPreprocessor()
        
    def transcribe_meeting(self, audio_file_path: str, 
                          speaker_diarization: bool = False,
                          meeting_context: Dict = None) -> Dict:
        """Transcribe meeting audio with speaker identification and context"""
        
        # Preprocess audio
        processed_audio = self.preprocessor.preprocess_audio(audio_file_path)
        
        # Transcribe with timestamps
        result = self.whisper_manager.model.transcribe(
            processed_audio,
            **self.whisper_manager.default_options,
            word_timestamps=True,
            verbose=True
        )
        
        # Process segments for meeting format
        meeting_transcript = self._format_meeting_transcript(result, meeting_context)
        
        # Add speaker diarization if requested
        if speaker_diarization:
            meeting_transcript = self._add_speaker_diarization(meeting_transcript, processed_audio)
        
        return meeting_transcript
    
    def _format_meeting_transcript(self, whisper_result: Dict, context: Dict = None) -> Dict:
        """Format Whisper output for meeting documentation"""
        
        segments = []
        for segment in whisper_result["segments"]:
            formatted_segment = {
                "start_time": self._format_timestamp(segment["start"]),
                "end_time": self._format_timestamp(segment["end"]),
                "text": segment["text"].strip(),
                "confidence": getattr(segment, "confidence", 0.0),
                "words": [
                    {
                        "word": word["word"],
                        "start": word["start"],
                        "end": word["end"],
                        "confidence": word.get("probability", 0.0)
                    }
                    for word in segment.get("words", [])
                ]
            }
            segments.append(formatted_segment)
        
        meeting_data = {
            "meeting_info": context or {},
            "full_text": whisper_result["text"],
            "language": whisper_result["language"],
            "segments": segments,
            "duration": segments[-1]["end_time"] if segments else "00:00:00",
            "word_count": len(whisper_result["text"].split()),
            "confidence_score": np.mean([seg.get("confidence", 0) for seg in segments])
        }
        
        return meeting_data
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _add_speaker_diarization(self, transcript: Dict, audio: np.ndarray) -> Dict:
        """Add speaker identification to transcript"""
        # This is a placeholder for speaker diarization
        # In production, integrate with libraries like pyannote.audio
        
        # Simple speaker change detection based on pause length
        segments = transcript["segments"]
        current_speaker = "Speaker 1"
        speaker_counter = 1
        
        for i, segment in enumerate(segments):
            if i > 0:
                pause_duration = segment["start_time"] - segments[i-1]["end_time"]
                if pause_duration > 2.0:  # 2 second pause indicates speaker change
                    speaker_counter += 1
                    current_speaker = f"Speaker {speaker_counter}"
            
            segment["speaker"] = current_speaker
        
        return transcript
```

### Real-time Voice Processing
```python
class RealTimeVoiceProcessor:
    def __init__(self, whisper_manager: WhisperManager):
        self.whisper_manager = whisper_manager
        self.audio_buffer = []
        self.buffer_duration = 10  # seconds
        self.sample_rate = 16000
        
    async def process_audio_stream(self, audio_chunk: bytes) -> Optional[str]:
        """Process streaming audio for real-time transcription"""
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(audio_chunk, dtype=np.float32)
        
        # Add to buffer
        self.audio_buffer.extend(audio_data)
        
        # Check if buffer has enough data
        required_samples = self.buffer_duration * self.sample_rate
        if len(self.audio_buffer) >= required_samples:
            
            # Extract chunk for processing
            chunk_data = np.array(self.audio_buffer[:required_samples])
            
            # Transcribe chunk
            result = await self._transcribe_chunk_async(chunk_data)
            
            # Remove processed data from buffer (with overlap)
            overlap_samples = self.sample_rate * 2  # 2 second overlap
            self.audio_buffer = self.audio_buffer[required_samples - overlap_samples:]
            
            return result
        
        return None
    
    async def _transcribe_chunk_async(self, audio_chunk: np.ndarray) -> str:
        """Asynchronously transcribe audio chunk"""
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._transcribe_chunk,
            audio_chunk
        )
        
        return result
    
    def _transcribe_chunk(self, audio_chunk: np.ndarray) -> str:
        """Transcribe single audio chunk"""
        
        # Use faster, less accurate settings for real-time processing
        options = self.whisper_manager.default_options.copy()
        options.update({
            "beam_size": 1,
            "best_of": 1,
            "temperature": 0.0,
            "without_timestamps": True,
            "word_timestamps": False
        })
        
        result = self.whisper_manager.model.transcribe(audio_chunk, **options)
        return result["text"].strip()
```

### Meeting Summary Generation
```python
class MeetingSummarizer:
    def __init__(self, whisper_manager: WhisperManager, llm_service):
        self.whisper_manager = whisper_manager
        self.llm_service = llm_service
        
    def generate_meeting_summary(self, meeting_transcript: Dict, 
                                meeting_type: str = "general") -> Dict:
        """Generate comprehensive meeting summary from transcript"""
        
        # Extract key information
        full_text = meeting_transcript["full_text"]
        segments = meeting_transcript["segments"]
        duration = meeting_transcript["duration"]
        
        # Generate different types of summaries
        summaries = {
            "executive_summary": self._generate_executive_summary(full_text),
            "detailed_summary": self._generate_detailed_summary(segments),
            "action_items": self._extract_action_items(full_text),
            "key_decisions": self._extract_key_decisions(full_text),
            "participants": self._identify_participants(segments),
            "topics_discussed": self._extract_topics(full_text)
        }
        
        # Generate final report
        meeting_report = {
            "meeting_metadata": {
                "duration": duration,
                "word_count": meeting_transcript["word_count"],
                "confidence_score": meeting_transcript["confidence_score"],
                "meeting_type": meeting_type,
                "generated_at": datetime.now().isoformat()
            },
            "summaries": summaries,
            "full_transcript": meeting_transcript
        }
        
        return meeting_report
    
    def _generate_executive_summary(self, full_text: str) -> str:
        """Generate executive summary using LLM"""
        
        prompt = f"""다음 회의 내용을 바탕으로 경영진을 위한 간단한 요약을 작성해주세요.
주요 논의사항, 결정사항, 후속조치를 포함하여 3-5문장으로 요약해주세요.

회의 내용:
{full_text}

경영진 요약:"""
        
        summary = self.llm_service.generate(prompt)
        return summary
    
    def _generate_detailed_summary(self, segments: List[Dict]) -> str:
        """Generate detailed summary with timeline"""
        
        # Group segments by topic/speaker
        summary_parts = []
        
        for segment in segments:
            timestamp = segment["start_time"]
            text = segment["text"]
            speaker = segment.get("speaker", "참가자")
            
            summary_parts.append(f"[{timestamp}] {speaker}: {text}")
        
        return "\n".join(summary_parts)
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from meeting text"""
        
        prompt = f"""다음 회의 내용에서 후속조치 사항들을 추출해주세요.
각 항목은 담당자와 마감일이 언급된 경우 함께 포함해주세요.

회의 내용:
{text}

후속조치 사항:"""
        
        action_items_text = self.llm_service.generate(prompt)
        
        # Parse into list
        action_items = [item.strip() for item in action_items_text.split('\n') if item.strip()]
        return action_items
    
    def _extract_key_decisions(self, text: str) -> List[str]:
        """Extract key decisions made during meeting"""
        
        prompt = f"""다음 회의 내용에서 내려진 주요 결정사항들을 추출해주세요.

회의 내용:
{text}

주요 결정사항:"""
        
        decisions_text = self.llm_service.generate(prompt)
        decisions = [item.strip() for item in decisions_text.split('\n') if item.strip()]
        return decisions
    
    def _identify_participants(self, segments: List[Dict]) -> List[str]:
        """Identify meeting participants from segments"""
        
        speakers = set()
        for segment in segments:
            speaker = segment.get("speaker")
            if speaker:
                speakers.add(speaker)
        
        return list(speakers)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics discussed"""
        
        prompt = f"""다음 회의 내용에서 논의된 주요 주제들을 추출해주세요.

회의 내용:
{text}

주요 논의 주제:"""
        
        topics_text = self.llm_service.generate(prompt)
        topics = [item.strip() for item in topics_text.split('\n') if item.strip()]
        return topics
```

### Quality Assurance and Validation
```python
class TranscriptionQualityAssurance:
    def __init__(self):
        self.confidence_threshold = 0.8
        self.min_speech_ratio = 0.3
        
    def validate_transcription(self, transcript: Dict, audio_file: str) -> Dict:
        """Validate transcription quality and provide confidence metrics"""
        
        validation_results = {
            "overall_quality": "good",
            "confidence_score": transcript.get("confidence_score", 0.0),
            "issues": [],
            "recommendations": []
        }
        
        # Check confidence scores
        if validation_results["confidence_score"] < self.confidence_threshold:
            validation_results["issues"].append("Low confidence score")
            validation_results["recommendations"].append("Consider re-recording with better audio quality")
        
        # Check for audio quality issues
        audio_quality = self._assess_audio_quality(audio_file)
        if audio_quality["noise_level"] > 0.3:
            validation_results["issues"].append("High noise level detected")
            validation_results["recommendations"].append("Use noise reduction in future recordings")
        
        # Check speech-to-silence ratio
        speech_ratio = self._calculate_speech_ratio(transcript)
        if speech_ratio < self.min_speech_ratio:
            validation_results["issues"].append("Low speech content ratio")
            validation_results["recommendations"].append("Remove long silent periods")
        
        # Determine overall quality
        if len(validation_results["issues"]) == 0:
            validation_results["overall_quality"] = "excellent"
        elif len(validation_results["issues"]) <= 2:
            validation_results["overall_quality"] = "good"
        else:
            validation_results["overall_quality"] = "poor"
        
        return validation_results
    
    def _assess_audio_quality(self, audio_file: str) -> Dict:
        """Assess audio file quality metrics"""
        
        audio, sr = librosa.load(audio_file)
        
        # Calculate noise level (simplified)
        rms_energy = librosa.feature.rms(y=audio)[0]
        noise_level = np.min(rms_energy) / np.max(rms_energy)
        
        # Calculate dynamic range
        dynamic_range = np.max(audio) - np.min(audio)
        
        return {
            "noise_level": noise_level,
            "dynamic_range": dynamic_range,
            "sample_rate": sr,
            "duration": len(audio) / sr
        }
    
    def _calculate_speech_ratio(self, transcript: Dict) -> float:
        """Calculate ratio of speech to total audio duration"""
        
        segments = transcript.get("segments", [])
        if not segments:
            return 0.0
        
        total_speech_duration = sum(
            float(seg["end_time"].split(":")[2]) - float(seg["start_time"].split(":")[2])
            for seg in segments
        )
        
        total_duration = float(transcript.get("duration", "00:00:00").split(":")[2])
        
        return total_speech_duration / max(total_duration, 1.0)
```

### Integration with ex-GPT Workflow
```python
class STTWorkflowIntegration:
    def __init__(self, whisper_manager: WhisperManager, email_service, document_service):
        self.whisper_manager = whisper_manager
        self.email_service = email_service
        self.document_service = document_service
        self.meeting_transcriber = MeetingTranscriber(whisper_manager)
        self.meeting_summarizer = MeetingSummarizer(whisper_manager, None)  # LLM service to be injected
        
    async def process_meeting_workflow(self, audio_file_path: str, 
                                     meeting_metadata: Dict,
                                     recipient_email: str) -> Dict:
        """Complete workflow: transcribe -> summarize -> generate report -> send email"""
        
        try:
            # Step 1: Transcribe meeting
            transcript = self.meeting_transcriber.transcribe_meeting(
                audio_file_path, 
                speaker_diarization=True,
                meeting_context=meeting_metadata
            )
            
            # Step 2: Generate meeting summary
            meeting_report = self.meeting_summarizer.generate_meeting_summary(
                transcript,
                meeting_metadata.get("meeting_type", "general")
            )
            
            # Step 3: Create document
            document_path = await self._create_meeting_document(meeting_report)
            
            # Step 4: Send email with report
            await self._send_meeting_report_email(
                recipient_email,
                meeting_report,
                document_path
            )
            
            # Step 5: Store in document management system
            document_id = await self.document_service.store_document(
                document_path,
                metadata={
                    "type": "meeting_report",
                    "meeting_date": meeting_metadata.get("date"),
                    "participants": meeting_report["summaries"]["participants"]
                }
            )
            
            return {
                "status": "success",
                "document_id": document_id,
                "transcript_confidence": transcript["confidence_score"],
                "report_path": document_path
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_meeting_document(self, meeting_report: Dict) -> str:
        """Create formatted meeting document"""
        
        # Generate markdown document
        markdown_content = self._format_meeting_report_markdown(meeting_report)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_report_{timestamp}.md"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def _format_meeting_report_markdown(self, meeting_report: Dict) -> str:
        """Format meeting report as markdown"""
        
        metadata = meeting_report["meeting_metadata"]
        summaries = meeting_report["summaries"]
        
        markdown = f"""# 회의록
        
## 회의 정보
- 회의 시간: {metadata["duration"]}
- 단어 수: {metadata["word_count"]}
- 신뢰도: {metadata["confidence_score"]:.2f}
- 생성 일시: {metadata["generated_at"]}

## 요약

### 경영진 요약
{summaries["executive_summary"]}

### 주요 결정사항
"""
        
        for decision in summaries["key_decisions"]:
            markdown += f"- {decision}\n"
        
        markdown += "\n### 후속조치 사항\n"
        for action in summaries["action_items"]:
            markdown += f"- {action}\n"
        
        markdown += "\n### 참석자\n"
        for participant in summaries["participants"]:
            markdown += f"- {participant}\n"
        
        markdown += "\n### 논의 주제\n"
        for topic in summaries["topics_discussed"]:
            markdown += f"- {topic}\n"
        
        return markdown
    
    async def _send_meeting_report_email(self, recipient: str, report: Dict, document_path: str):
        """Send meeting report via email"""
        
        subject = f"회의록 - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""안녕하세요,
        
요청하신 회의록이 자동으로 생성되었습니다.

주요 정보:
- 회의 시간: {report["meeting_metadata"]["duration"]}
- 신뢰도: {report["meeting_metadata"]["confidence_score"]:.2f}

첨부된 문서를 확인해주세요.

감사합니다.
ex-GPT 시스템"""
        
        await self.email_service.send_email(
            to=recipient,
            subject=subject,
            body=body,
            attachments=[document_path]
        )
```
