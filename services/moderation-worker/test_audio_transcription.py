"""
Test script for audio transcription with Whisper.
Run this directly to test audio file transcription without the full worker pipeline.

Usage:
    python test_audio_transcription.py <path_to_audio_file>

Example:
    python test_audio_transcription.py /path/to/test.mp3
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_whisper_directly(audio_path: str, model_size: str = "base"):
    """Test Whisper transcription directly"""
    import whisper
    
    logger.info(f"=== Testing Whisper Model ===")
    logger.info(f"Audio file: {audio_path}")
    logger.info(f"Model size: {model_size}")
    
    # Check file
    if not os.path.exists(audio_path):
        logger.error(f"File not found: {audio_path}")
        return None
    
    file_size = os.path.getsize(audio_path)
    logger.info(f"File size: {file_size} bytes ({file_size/1024:.1f} KB)")
    
    # Get file extension
    _, ext = os.path.splitext(audio_path)
    logger.info(f"File extension: {ext}")
    
    # Load model
    logger.info(f"Loading Whisper model '{model_size}'...")
    try:
        model = whisper.load_model(model_size, device="cpu")
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None
    
    # Transcribe
    logger.info("Starting transcription...")
    try:
        result = model.transcribe(
            audio_path,
            language='vi',
            task='transcribe',
            fp16=False,  # CPU mode
            verbose=True  # Show progress
        )
        
        transcribed_text = result['text'].strip()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TRANSCRIPTION RESULT")
        logger.info(f"{'='*60}")
        logger.info(f"Text: '{transcribed_text}'")
        logger.info(f"Language: {result.get('language', 'unknown')}")
        
        if result.get('segments'):
            logger.info(f"\nSegments ({len(result['segments'])} total):")
            for seg in result['segments']:
                logger.info(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        
        logger.info(f"{'='*60}")
        
        return transcribed_text
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return None


def test_full_pipeline(audio_path: str):
    """Test the full AudioModerationInference pipeline"""
    from audio.inference_audio import AudioModerationInference
    
    # Create a mock text moderator for testing
    class MockTextModerator:
        def predict(self, text):
            logger.info(f"[MockModerator] Received text: '{text[:100]}...'")
            return {
                'moderation_result': 'allowed',
                'sentiment': 'positive',
                'confidence': 0.95,
                'reasoning': 'Test moderation - text looks fine'
            }
    
    logger.info(f"\n{'='*60}")
    logger.info("Testing Full Audio Moderation Pipeline")
    logger.info(f"{'='*60}")
    
    try:
        # Initialize with base model
        audio_mod = AudioModerationInference(
            model_size="base",
            device="cpu",
            text_moderator=MockTextModerator()
        )
        
        result = audio_mod.predict(audio_path)
        
        logger.info(f"\n{'='*60}")
        logger.info("FULL PIPELINE RESULT")
        logger.info(f"{'='*60}")
        for key, value in result.items():
            logger.info(f"  {key}: {value}")
        logger.info(f"{'='*60}")
        
        return result
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}", exc_info=True)
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nNo audio file specified. Looking for test files...")
        
        # Try to find test audio files
        test_files = []
        for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            for root, dirs, files in os.walk('.'):
                for f in files:
                    if f.endswith(ext):
                        test_files.append(os.path.join(root, f))
        
        if test_files:
            print(f"\nFound {len(test_files)} audio file(s):")
            for f in test_files[:5]:
                print(f"  - {f}")
            
            audio_path = test_files[0]
            print(f"\nUsing first file: {audio_path}")
        else:
            print("\nNo audio files found. Please provide an audio file path.")
            sys.exit(1)
    else:
        audio_path = sys.argv[1]
    
    # Test 1: Direct Whisper test
    print("\n" + "="*60)
    print("TEST 1: Direct Whisper Transcription")
    print("="*60)
    result1 = test_whisper_directly(audio_path, model_size="base")
    
    if result1:
        print(f"\n✅ Direct transcription successful!")
        print(f"   Result: '{result1[:100]}...'")
    else:
        print(f"\n❌ Direct transcription failed!")
    
    # Test 2: Full pipeline test
    print("\n" + "="*60)
    print("TEST 2: Full Audio Moderation Pipeline")
    print("="*60)
    result2 = test_full_pipeline(audio_path)
    
    if result2 and result2.get('transcribed_text'):
        print(f"\n✅ Full pipeline successful!")
        print(f"   Transcribed: '{result2.get('transcribed_text', '')[:100]}...'")
        print(f"   Moderation: {result2.get('moderation_result')}")
    else:
        print(f"\n❌ Full pipeline failed or no text transcribed!")


if __name__ == "__main__":
    main()
