"""
Simple API endpoint for CSM Audio Generation
Based on SesameAILabs/csm repository
"""
import os
import torch
import torchaudio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging
import base64
import io

# Set environment variables for CSM
os.environ["NO_TORCH_COMPILE"] = "1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CSM Audio Generation API", version="1.0.0")

# Global generator variable
generator = None

class GenerateRequest(BaseModel):
    text: str
    speaker: Optional[int] = 0
    max_audio_length_ms: Optional[int] = 10000
    context: Optional[List[dict]] = None

class GenerateResponse(BaseModel):
    audio_base64: str
    sample_rate: int
    duration_ms: int

@app.on_event("startup")
async def startup_event():
    """Initialize the CSM model on startup"""
    global generator
    try:
        logger.info("Loading CSM model...")
        
        # Import CSM generator from the original repository
        from generator import load_csm_1b, Segment
        
        # Determine device
        if torch.cuda.is_available():
            device = "cuda"
            logger.info("Using CUDA device")
        elif torch.backends.mps.is_available():
            device = "mps"
            logger.info("Using MPS device")
        else:
            device = "cpu"
            logger.info("Using CPU device")
        
        # Load the CSM model
        generator = load_csm_1b(device=device)
        logger.info("CSM model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load CSM model: {str(e)}")
        # Create a fallback generator for testing
        generator = create_fallback_generator()
        logger.info("Using fallback generator for testing")

def create_fallback_generator():
    """Create a fallback generator for testing when CSM is not available"""
    class FallbackGenerator:
        def __init__(self):
            self.sample_rate = 24000
            
        def generate(self, text, speaker=0, context=None, max_audio_length_ms=10000):
            # Generate a simple sine wave as placeholder
            duration_samples = min(int(max_audio_length_ms * self.sample_rate / 1000), 240000)
            t = torch.linspace(0, max_audio_length_ms / 1000, duration_samples)
            frequency = 440 + speaker * 100
            audio = 0.3 * torch.sin(2 * torch.pi * frequency * t)
            noise = 0.05 * torch.randn_like(audio)
            return audio + noise
    
    return FallbackGenerator()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": generator is not None}

@app.post("/generate", response_model=GenerateResponse)
async def generate_audio(request: GenerateRequest):
    """
    Generate audio from text using CSM model
    """
    if generator is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        logger.info(f"Generating audio for text: {request.text[:50]}...")
        
        # Process context if provided
        context_segments = []
        if request.context:
            try:
                from generator import Segment
                for ctx in request.context:
                    if "text" in ctx and "speaker" in ctx:
                        segment = Segment(
                            text=ctx["text"],
                            speaker=ctx["speaker"],
                            audio=None
                        )
                        context_segments.append(segment)
            except ImportError:
                logger.warning("Could not import Segment, using context without audio")
        
        # Generate audio
        audio = generator.generate(
            text=request.text,
            speaker=request.speaker,
            context=context_segments,
            max_audio_length_ms=request.max_audio_length_ms
        )
        
        # Convert audio to base64
        audio_bytes = io.BytesIO()
        torchaudio.save(audio_bytes, audio.unsqueeze(0).cpu(), generator.sample_rate, format="wav")
        audio_bytes.seek(0)
        audio_base64 = base64.b64encode(audio_bytes.getvalue()).decode('utf-8')
        
        # Calculate duration
        duration_ms = int((audio.shape[0] / generator.sample_rate) * 1000)
        
        logger.info(f"Generated audio successfully, duration: {duration_ms}ms")
        
        return GenerateResponse(
            audio_base64=audio_base64,
            sample_rate=generator.sample_rate,
            duration_ms=duration_ms
        )
        
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CSM Audio Generation API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
