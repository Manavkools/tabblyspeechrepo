# CSM 1B Audio Generation API

A FastAPI-based service that provides audio generation using the CSM (Conversational Speech Model) 1B model from Sesame AI Labs. This service is designed for deployment on RunPod serverless infrastructure.

## Features

- 🎵 High-quality speech generation using CSM 1B model
- 🚀 FastAPI-based REST API
- 🐳 Docker containerization for easy deployment
- ☁️ RunPod serverless support
- 🎯 Simple text-to-speech conversion
- 🔄 Context-aware conversation support

## API Endpoints

### POST /generate

Generate audio from text input.

**Request Body:**
```json
{
  "text": "Hello, this is a test of the CSM audio generation.",
  "speaker": 0,
  "max_audio_length_ms": 10000,
  "context": [
    {
      "text": "Previous conversation context",
      "speaker": 1
    }
  ]
}
```

**Response:**
```json
{
  "audio_base64": "base64_encoded_audio_data",
  "sample_rate": 24000,
  "duration_ms": 5000
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## Local Development

### Prerequisites

- Python 3.10+
- CUDA-compatible GPU (recommended)
- Docker (for containerized deployment)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd tabblyttspipeline
```

2. Create and activate virtual environment:
```bash
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export NO_TORCH_COMPILE=1
```

5. Login to Hugging Face (required for model access):
```bash
huggingface-cli login
```

6. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Build the Docker image:
```bash
docker build -t csm-audio-api .
```

### Run the container:
```bash
docker run -p 8000:8000 --gpus all csm-audio-api
```

## RunPod Serverless Deployment

### Prerequisites

1. RunPod account with serverless credits
2. Docker image pushed to a registry (Docker Hub, etc.)

### Deployment Steps

1. **Build and push Docker image:**
```bash
# Build the image
docker build -t your-username/csm-audio-api:latest .

# Push to registry
docker push your-username/csm-audio-api:latest
```

2. **Create RunPod serverless endpoint:**
   - Go to RunPod console
   - Create new serverless endpoint
   - Use your Docker image
   - Set the following configuration:
     - Runtime: Python 3.10
     - Handler: `runpod_handler.handler`
     - Memory: 8GB
     - GPU: A10G or similar
     - Timeout: 300 seconds

3. **Test the endpoint:**
```bash
curl -X POST "https://your-endpoint-url.runpod.ai" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello from RunPod!",
      "speaker": 0,
      "max_audio_length_ms": 5000
    }
  }'
```

## Usage Examples

### Python Client

```python
import requests
import base64
import io
import torchaudio

# API endpoint
url = "https://your-endpoint-url.runpod.ai"

# Request data
data = {
    "input": {
        "text": "Hello, this is a test of the CSM audio generation system.",
        "speaker": 0,
        "max_audio_length_ms": 10000
    }
}

# Make request
response = requests.post(url, json=data)
result = response.json()

# Decode and save audio
if "audio_base64" in result:
    audio_data = base64.b64decode(result["audio_base64"])
    
    # Save to file
    with open("generated_audio.wav", "wb") as f:
        f.write(audio_data)
    
    print(f"Audio generated successfully!")
    print(f"Duration: {result['duration_ms']}ms")
    print(f"Sample rate: {result['sample_rate']}Hz")
```

### cURL Example

```bash
curl -X POST "https://your-endpoint-url.runpod.ai" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello, this is a test of the CSM audio generation system.",
      "speaker": 0,
      "max_audio_length_ms": 10000
    }
  }' \
  --output response.json
```

## Model Information

- **Model**: CSM 1B (Conversational Speech Model)
- **Provider**: Sesame AI Labs
- **Architecture**: Llama backbone with audio decoder
- **Sample Rate**: 24kHz
- **Format**: WAV audio output

## Requirements

- CUDA-compatible GPU (recommended)
- Python 3.10+
- 8GB+ RAM
- Access to Hugging Face models:
  - `meta-llama/Llama-3.2-1B`
  - `SesameAILabs/CSM-1B`

## Troubleshooting

### Common Issues

1. **Model loading errors**: Ensure you have access to the required Hugging Face models
2. **CUDA out of memory**: Reduce `max_audio_length_ms` or use a smaller model
3. **Audio quality issues**: Try different speaker IDs (0-1) or provide context

### Logs

Check the application logs for detailed error information:
```bash
docker logs <container-id>
```

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Sesame AI Labs](https://github.com/SesameAILabs/csm) for the CSM model
- [RunPod](https://runpod.io) for serverless infrastructure
- [FastAPI](https://fastapi.tiangolo.com) for the web framework
