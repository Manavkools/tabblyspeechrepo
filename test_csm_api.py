"""
Test script for CSM Audio Generation API
"""
import requests
import base64
import json
import time

def test_csm_api():
    """Test the CSM API endpoint"""
    url = "http://localhost:8000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{url}/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test generate endpoint
    print("\nTesting generate endpoint...")
    data = {
        "text": "Hello, this is a test of the CSM audio generation system.",
        "speaker": 0,
        "max_audio_length_ms": 5000
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{url}/generate", json=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generation successful!")
            print(f"Duration: {result['duration_ms']}ms")
            print(f"Sample rate: {result['sample_rate']}Hz")
            print(f"Response time: {end_time - start_time:.2f}s")
            
            # Save audio file
            audio_data = base64.b64decode(result['audio_base64'])
            with open("csm_test_output.wav", "wb") as f:
                f.write(audio_data)
            print("Audio saved as csm_test_output.wav")
            
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("CSM Audio Generation API Test")
    print("=" * 40)
    test_csm_api()
