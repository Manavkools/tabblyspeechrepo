"""
RunPod serverless handler for CSM 1B Audio Generation
"""
import json
import base64
import io
import torch
import torchaudio
from generator import load_csm_1b
import logging

# Initialize generator globally
generator = None

def initialize_generator():
    """Initialize the CSM generator"""
    global generator
    if generator is None:
        try:
            # Determine device
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
            
            generator = load_csm_1b(device=device)
            logging.info("CSM 1B model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load CSM 1B model: {str(e)}")
            raise e

logger = logging.getLogger(__name__)

def handler(event):
    """
    RunPod serverless handler function
    
    Args:
        event: Dictionary containing the request data
        
    Returns:
        Dictionary containing the response
    """
    try:
        # Initialize generator if not already done
        initialize_generator()
        
        # Parse the input
        input_data = event.get("input", {})
        
        # Extract parameters
        text = input_data.get("text", "")
        speaker = input_data.get("speaker", 0)
        max_audio_length_ms = input_data.get("max_audio_length_ms", 10000)
        context = input_data.get("context", None)
        
        if not text:
            return {
                "error": "No text provided",
                "statusCode": 400
            }
        
        # Process context if provided
        context_segments = []
        if context:
            for ctx in context:
                if "text" in ctx and "speaker" in ctx:
                    from generator import Segment
                    segment = Segment(
                        text=ctx["text"],
                        speaker=ctx["speaker"],
                        audio=None
                    )
                    context_segments.append(segment)
        
        # Generate audio
        audio = generator.generate(
            text=text,
            speaker=speaker,
            context=context_segments,
            max_audio_length_ms=max_audio_length_ms
        )
        
        # Convert audio to base64
        audio_bytes = io.BytesIO()
        torchaudio.save(audio_bytes, audio.unsqueeze(0).cpu(), generator.sample_rate, format="wav")
        audio_bytes.seek(0)
        audio_base64 = base64.b64encode(audio_bytes.getvalue()).decode('utf-8')
        
        # Calculate duration
        duration_ms = int((audio.shape[0] / generator.sample_rate) * 1000)
        
        # Return response
        return {
            "audio_base64": audio_base64,
            "sample_rate": generator.sample_rate,
            "duration_ms": duration_ms,
            "statusCode": 200
        }
        
    except Exception as e:
        logger.error(f"Error in RunPod handler: {str(e)}")
        return {
            "error": str(e),
            "statusCode": 500
        }
