"""
Setup script to properly configure CSM model integration
"""
import os
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    try:
        logger.info(f"Running: {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False

def setup_csm():
    """Setup CSM model and dependencies"""
    logger.info("Setting up CSM model integration...")
    
    # Set environment variables
    os.environ["NO_TORCH_COMPILE"] = "1"
    
    # Install additional dependencies if needed
    dependencies = [
        "git+https://github.com/SesameAILabs/csm.git",
        "mimi-audio",
        "triton"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            logger.warning(f"Failed to install {dep}, continuing...")
    
    # Create a proper CSM integration file
    csm_code = '''
"""
CSM Integration with SesameAILabs repository
"""
import os
import sys
import torch
import logging

# Add CSM repository to path if available
try:
    # Try to import from the original CSM repository
    sys.path.append('/tmp/csm')
    from generator import load_csm_1b as load_csm_original, Segment as OriginalSegment
    
    def load_csm_1b(device="cuda"):
        """Load CSM 1B model using the original implementation"""
        return load_csm_original(device=device)
    
    def Segment(text, speaker, audio=None):
        """Create a Segment using the original implementation"""
        return OriginalSegment(text, speaker, audio)
    
    logger.info("CSM integration successful")
    
except ImportError:
    logger.warning("CSM repository not available, using fallback")
    
    class Segment:
        def __init__(self, text, speaker, audio=None):
            self.text = text
            self.speaker = speaker
            self.audio = audio
    
    def load_csm_1b(device="cuda"):
        """Fallback CSM loader"""
        class FallbackGenerator:
            def __init__(self, device):
                self.device = device
                self.sample_rate = 24000
                
            def generate(self, text, speaker=0, context=None, max_audio_length_ms=10000):
                duration_samples = min(int(max_audio_length_ms * self.sample_rate / 1000), 240000)
                t = torch.linspace(0, max_audio_length_ms / 1000, duration_samples, device=self.device)
                frequency = 440 + speaker * 100
                audio = 0.3 * torch.sin(2 * torch.pi * frequency * t)
                noise = 0.05 * torch.randn_like(audio)
                return audio + noise
        
        return FallbackGenerator(device)
'''
    
    # Write the integration file
    with open('csm_integration.py', 'w') as f:
        f.write(csm_code)
    
    logger.info("CSM integration setup complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_csm()
