"""
Test script for REAL image OCR moderation
Creates test images with text and runs moderation
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image_with_text(text, filename):
    """Create a simple test image with text"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create white background
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 72)
        except:
            font = ImageFont.load_default()
        
        # Draw text in center
        # Get text bbox
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width, text_height = 100, 50
        
        x = (400 - text_width) // 2
        y = (200 - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        img.save(filename)
        print(f"Created test image: {filename}")
        return filename
    except Exception as e:
        print(f"Failed to create test image: {e}")
        return None


def test_real_image_moderation():
    """Test with real generated images"""
    print("=" * 60)
    print("TEST: Real Image OCR Moderation")
    print("=" * 60)
    
    # Import the inference module
    from image.inference_image import ImageModerationInference
    
    # Initialize without text moderator (use critical word check only)
    print("\nLoading image moderation model...")
    model = ImageModerationInference(device='cpu', text_moderator=None)
    print("Model loaded!\n")
    
    # Test cases - (text, should_reject, description)
    test_cases = [
        ("NGU", True, "Single Vietnamese insult"),
        ("HELLO", False, "Normal English word"),
        ("VCL", True, "Vietnamese abbreviation slur"),
        ("SHOP", False, "Normal word"),
    ]
    
    passed = 0
    failed = 0
    temp_files = []
    
    for text, should_reject, description in test_cases:
        temp_file = f"test_img_{text.lower()}.png"
        temp_files.append(temp_file)
        
        print(f"\n{'='*40}")
        print(f"Testing: {description}")
        print(f"Text in image: '{text}'")
        print(f"Expected: {'REJECT' if should_reject else 'ALLOW'}")
        
        # Create test image
        img_path = create_test_image_with_text(text, temp_file)
        if not img_path:
            print("❌ Failed to create test image")
            failed += 1
            continue
        
        # Run moderation
        result = model.predict(img_path)
        
        print(f"\nResult:")
        print(f"  - moderation_result: {result.get('moderation_result')}")
        print(f"  - extracted_text: {result.get('extracted_text', 'N/A')}")
        print(f"  - reasoning: {result.get('reasoning', 'N/A')}")
        
        is_rejected = result.get('moderation_result') == 'reject'
        
        if is_rejected == should_reject:
            print(f"\n✅ PASS")
            passed += 1
        else:
            print(f"\n❌ FAIL - Expected {'reject' if should_reject else 'allowed'}, got {result.get('moderation_result')}")
            failed += 1
    
    # Cleanup temp files
    for f in temp_files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def main():
    print("\n" + "=" * 60)
    print("REAL IMAGE OCR MODERATION TEST")
    print("=" * 60 + "\n")
    
    try:
        success = test_real_image_moderation()
        if success:
            print("\n🎉 ALL REAL IMAGE TESTS PASSED!")
            return 0
        else:
            print("\n⚠️ SOME TESTS FAILED")
            return 1
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
