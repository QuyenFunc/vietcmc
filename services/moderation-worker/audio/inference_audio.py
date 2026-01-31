import whisper
import os
import logging
import torch
import re

logger = logging.getLogger(__name__)

# Common Whisper transcription errors for Vietnamese
# Maps incorrect transcription -> correct word
VIETNAMESE_CORRECTIONS = {
    # Tone/diacritic errors for "ngu" (stupid)
    'ngù': 'ngu',
    'ngú': 'ngu', 
    'ngủ': 'ngu',  # Context-dependent, but often mistranscribed
    'ngư': 'ngu',
    'ngưu': 'ngu',
    'ngừ': 'ngu',
    
    # Common word confusions
    'mấy': 'mày',  # Often confused in context
    'mẩy': 'mày',
    'mảy': 'mày',
    
    # "sao" vs other words  
    'sau': 'sao',  # Context: "sao mày" not "sau mấy"
    
    # Other common errors
    'đụ': 'địt',   # Vulgar word often mistranscribed
    'đù': 'địt',
    'đụ má': 'địt mẹ',
    'đù má': 'địt mẹ',
    
    # Insults
    'ngốc': 'ngu',  # Sometimes these are related
    'đần': 'đần',
    'khùng': 'khùng',
    'điên': 'điên',
}

# Context-aware corrections (phrase level)
PHRASE_CORRECTIONS = [
    # Pattern: (regex pattern, replacement)
    (r'\bsau\s+mấy\b', 'sao mày'),
    (r'\bsau\s+mày\b', 'sao mày'),
    (r'\bngù\s+thế\b', 'ngu thế'),
    (r'\bngưu\s+thế\b', 'ngu thế'),
    (r'\bngù\s+quá\b', 'ngu quá'),
    (r'\bngưu\s+quá\b', 'ngu quá'),
    (r'\bngù\s+vậy\b', 'ngu vậy'),
    (r'\bngưu\s+vậy\b', 'ngu vậy'),
    (r'\bđồ\s+ngù\b', 'đồ ngu'),
    (r'\bđồ\s+ngưu\b', 'đồ ngu'),
    (r'\bthằng\s+ngù\b', 'thằng ngu'),
    (r'\bthằng\s+ngưu\b', 'thằng ngu'),
    (r'\bcon\s+ngù\b', 'con ngu'),
    (r'\bcon\s+ngưu\b', 'con ngu'),
]


def post_process_vietnamese(text: str) -> str:
    """
    Post-process Whisper transcription to fix common Vietnamese errors.
    """
    if not text:
        return text
    
    original = text
    corrected = text.lower()  # Work with lowercase for matching
    
    # Apply phrase-level corrections first (more specific)
    for pattern, replacement in PHRASE_CORRECTIONS:
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
    
    # Apply word-level corrections
    for wrong, right in VIETNAMESE_CORRECTIONS.items():
        # Use word boundary to avoid partial matches
        pattern = r'\b' + re.escape(wrong) + r'\b'
        corrected = re.sub(pattern, right, corrected, flags=re.IGNORECASE)
    
    # Restore original capitalization for first character
    if original and original[0].isupper():
        corrected = corrected[0].upper() + corrected[1:] if len(corrected) > 1 else corrected.upper()
    
    if corrected != original.lower():
        logger.info(f"[AudioInference] Post-processed: '{original}' -> '{corrected}'")
    
    return corrected


class AudioModerationInference:
    def __init__(self, model_size="small", device="cpu", text_moderator=None):
        self.device = device
        self.model_size = model_size
        self.model = None
        self.text_moderator = text_moderator
        self.load_model()
        
    def load_model(self):
        try:
            logger.info(f"Loading Whisper model ({self.model_size}) on device '{self.device}'...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"Whisper model '{self.model_size}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
            
    def predict(self, audio_path: str):
        try:
            logger.info(f"[AudioInference] Processing audio: {audio_path}")
            
            # Check if file exists
            if isinstance(audio_path, str) and not audio_path.startswith('http'):
                if not os.path.exists(audio_path):
                    logger.error(f"[AudioInference] Audio file not found: {audio_path}")
                    return {
                        'moderation_result': 'review',
                        'sentiment': 'neutral',
                        'confidence': 0.0,
                        'reasoning': f"Audio file not found: {audio_path}",
                        'transcribed_text': ""
                    }
                
                file_size = os.path.getsize(audio_path)
                logger.info(f"[AudioInference] Audio file size: {file_size} bytes")
                
                if file_size < 1000:  # Less than 1KB
                    logger.warning(f"[AudioInference] Audio file is very small ({file_size} bytes)")
            
            # Transcribe with optimized settings for Vietnamese
            logger.info("[AudioInference] Starting Whisper transcription...")
            
            # Initial prompt with common Vietnamese words helps guide transcription
            initial_prompt = "Đây là tiếng Việt. Các từ phổ biến: ngu, mày, tao, địt, đụ, chửi, mẹ, bố, thằng, con."
            
            transcribe_options = {
                'language': 'vi',
                'task': 'transcribe',
                'verbose': False,
                'initial_prompt': initial_prompt,
            }
            
            # Disable fp16 on CPU to avoid issues
            if self.device == 'cpu':
                transcribe_options['fp16'] = False
            
            result = self.model.transcribe(audio_path, **transcribe_options)
            
            raw_text = result['text'].strip()
            
            # Log raw transcription
            logger.info(f"[AudioInference] Raw transcription: '{raw_text}'")
            logger.info(f"[AudioInference] Language detected: {result.get('language', 'unknown')}")
            
            # Apply Vietnamese post-processing
            transcribed_text = post_process_vietnamese(raw_text)
            
            # Log segments for debugging
            if 'segments' in result and result['segments']:
                for i, seg in enumerate(result['segments'][:3]):  # First 3 segments
                    logger.info(f"[AudioInference] Segment {i}: [{seg['start']:.1f}s-{seg['end']:.1f}s] '{seg['text']}'")
            else:
                logger.warning("[AudioInference] No segments found in transcription result")
            
            if not transcribed_text:
                logger.warning("[AudioInference] No speech detected in audio")
                return {
                    'moderation_result': 'allowed',
                    'sentiment': 'neutral',
                    'confidence': 1.0,
                    'reasoning': "No speech detected or audio too short/unclear",
                    'transcribed_text': ""
                }
            
            logger.info(f"[AudioInference] Final transcription: '{transcribed_text}'")
            
            # Moderate the text using existing text engine
            if self.text_moderator:
                logger.info("[AudioInference] Sending to text moderator...")
                text_result = self.text_moderator.predict(transcribed_text)
                
                # Enrich result
                text_result['transcribed_text'] = transcribed_text
                text_result['raw_transcription'] = raw_text  # Keep raw for debugging
                original_reasoning = text_result.get('reasoning', '')
                text_result['reasoning'] = f"[Audio] Extracted content: '{transcribed_text[:50]}...' | {original_reasoning}"
                
                logger.info(f"[AudioInference] Moderation result: {text_result.get('moderation_result')}")
                return text_result
            else:
                logger.warning("[AudioInference] No text moderator available")
                return {
                    'moderation_result': 'review',
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'reasoning': f"No text moderator available. Extracted content: '{transcribed_text}'",
                    'transcribed_text': transcribed_text
                }
                
        except Exception as e:
            logger.error(f"[AudioInference] Error processing audio {audio_path}: {e}", exc_info=True)
            return {
                'moderation_result': 'review',
                'sentiment': 'neutral',
                'label': 'error',
                'confidence': 0.0,
                'reasoning': f"Audio processing error: {str(e)}",
                'transcribed_text': ''
            }

