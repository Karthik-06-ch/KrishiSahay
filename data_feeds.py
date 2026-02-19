import random
import requests
import base64

def get_weather(city="Hyderabad"):
    """
    Mock weather data for demo purposes.
    In production, use OpenWeatherMap API key.
    """
    conditions = ["Sunny ☀️", "Cloudy ☁️", "Rainy 🌧️", "Windy 💨"]
    temp = random.randint(20, 35)
    condition = random.choice(conditions)
    humidity = random.randint(30, 80)
    return {
        "temp": temp,
        "condition": condition,
        "humidity": humidity,
        "city": city
    }

def get_market_prices():
    """Mock Mandi prices for demo."""
    return [
         {"crop": "Wheat", "price": "₹2125/qt"},
         {"crop": "Mustard", "price": "₹5450/qt"},
         {"crop": "Potato", "price": "₹1200/qt"},
         {"crop": "Cotton", "price": "₹6300/qt"},
    ]

def analyze_plant_image(image_bytes, model="moondream"):
    """
    Attempt to use Ollama's vision model (moondream or llava) to analyze the image.
    Fallback to a mock response if not available.
    """
    # Check if llava is available (we can reuse retrieval.get_available_models logic or just try)
    try:
        from config import OLLAMA_BASE_URL
        if not OLLAMA_BASE_URL:
             return "Error: OLLAMA_BASE_URL not set."

        # Convert bytes to base64 string
        img_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        payload = {
            "model": "moondream",  # Switching to moondream as it is faster/smaller
            "prompt": "Analyze this plant image. Is it healthy? If not, what disease does it have and how to treat it? Keep it simple.",
            "images": [img_b64],
            "stream": False
        }
        
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
             return resp.json().get("response", "No response from vision model.")
        elif resp.status_code == 404:
             return "⚠️ Model 'moondream' not found. Run `ollama pull moondream` to enable real image analysis.\n\n(Demo Result): The leaves show yellow spots, indicating early blight. Spray with Mancozeb."
    except Exception as e:
        return f"Error analyzing image: {e}"

    # Fallback/Demo Mock
    return "⚠️ Image Analysis Unavailable (Check logs). \n\n(Mock Result): Identified: Tomato Leaf Spot. Treatment: Apply Copper Fungicide."
