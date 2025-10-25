# CSM Audio Generation API - Deployment Guide

This guide will help you deploy the CSM 1B Audio Generation API to RunPod serverless.

## Prerequisites

1. **RunPod Account**: Sign up at [RunPod](https://runpod.io)
2. **Docker Hub Account**: For storing Docker images
3. **Hugging Face Account**: For accessing CSM models
4. **GitHub Account**: For version control

## Step 1: Prepare the Repository

### Clone and Setup

```bash
# Clone your repository
git clone <your-repo-url>
cd tabblyttspipeline

# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup CSM integration
python setup_csm.py
```

### Test Locally

```bash
# Test the API locally
python app.py

# In another terminal, test the API
python test_api.py
```

## Step 2: Build and Push Docker Image

### Build the Image

```bash
# Build the Docker image
docker build -t your-username/csm-audio-api:latest .

# Test the Docker image locally
docker run -p 8000:8000 --gpus all your-username/csm-audio-api:latest
```

### Push to Registry

```bash
# Login to Docker Hub
docker login

# Push the image
docker push your-username/csm-audio-api:latest
```

## Step 3: Deploy to RunPod Serverless

### Create RunPod Endpoint

1. Go to [RunPod Console](https://console.runpod.io)
2. Navigate to "Serverless" → "Endpoints"
3. Click "Create Endpoint"
4. Configure the endpoint:

```
Name: csm-audio-generator
Docker Image: your-username/csm-audio-api:latest
Runtime: Python 3.10
Handler: runpod_handler.handler
Memory: 8GB
GPU: A10G or similar
Timeout: 300 seconds
```

### Environment Variables

Set these environment variables in RunPod:

```
NO_TORCH_COMPILE=1
HF_TOKEN=your_huggingface_token
```

### Test the Endpoint

```bash
# Test the RunPod endpoint
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

## Step 4: Production Setup

### Model Access

1. **Hugging Face Setup**:
   - Get access to `SesameAILabs/CSM-1B` model
   - Get access to `meta-llama/Llama-3.2-1B` model
   - Set your HF token in RunPod environment variables

2. **Model Download**:
   - The models will be downloaded automatically on first run
   - This may take several minutes for the first request

### Monitoring

1. **Logs**: Check RunPod logs for any issues
2. **Metrics**: Monitor GPU usage and response times
3. **Errors**: Set up alerts for failed requests

## Step 5: API Usage

### Basic Usage

```python
import requests
import base64

# Your RunPod endpoint
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
    with open("generated_audio.wav", "wb") as f:
        f.write(audio_data)
    print("Audio generated successfully!")
```

### Advanced Usage with Context

```python
# Request with conversation context
data = {
    "input": {
        "text": "That sounds great!",
        "speaker": 1,
        "max_audio_length_ms": 8000,
        "context": [
            {
                "text": "How are you doing today?",
                "speaker": 0
            },
            {
                "text": "I'm doing well, thank you!",
                "speaker": 1
            }
        ]
    }
}
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**:
   - Check Hugging Face token
   - Verify model access permissions
   - Check GPU memory availability

2. **Docker Build Errors**:
   - Ensure all dependencies are in requirements.txt
   - Check Dockerfile syntax
   - Verify base image compatibility

3. **RunPod Deployment Issues**:
   - Check Docker image is accessible
   - Verify handler function name
   - Check memory and GPU requirements

### Debugging

1. **Local Testing**:
   ```bash
   # Test with verbose logging
   python app.py --log-level DEBUG
   ```

2. **Docker Testing**:
   ```bash
   # Run with logs
   docker run -p 8000:8000 --gpus all your-username/csm-audio-api:latest
   ```

3. **RunPod Logs**:
   - Check RunPod console for detailed logs
   - Monitor GPU usage and memory consumption

## Performance Optimization

### GPU Optimization

1. **Model Quantization**: Use FP16 for faster inference
2. **Batch Processing**: Process multiple requests together
3. **Caching**: Cache model in memory between requests

### Cost Optimization

1. **Cold Start**: Minimize cold start time
2. **Request Batching**: Combine multiple requests
3. **Auto-scaling**: Configure appropriate scaling policies

## Security Considerations

1. **API Keys**: Store securely in RunPod environment variables
2. **Rate Limiting**: Implement rate limiting for production
3. **Input Validation**: Validate all input parameters
4. **Error Handling**: Don't expose sensitive information in errors

## Monitoring and Maintenance

### Health Checks

```bash
# Check endpoint health
curl https://your-endpoint-url.runpod.ai/health
```

### Performance Monitoring

- Monitor response times
- Track GPU utilization
- Monitor memory usage
- Set up alerts for failures

### Regular Maintenance

1. **Model Updates**: Update to newer model versions
2. **Dependency Updates**: Keep dependencies current
3. **Security Patches**: Apply security updates regularly
4. **Performance Tuning**: Optimize based on usage patterns

## Support

For issues and questions:

1. **RunPod Support**: [RunPod Documentation](https://docs.runpod.io)
2. **CSM Model**: [SesameAILabs CSM Repository](https://github.com/SesameAILabs/csm)
3. **API Issues**: Check logs and error messages
4. **Performance Issues**: Monitor GPU and memory usage
