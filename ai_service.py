import google.generativeai as genai
import os
import json
from django.conf import settings
import PIL.Image

def configure_genai():
    api_key = os.environ.get("GOOGLE_API_KEY") or getattr(settings, 'GOOGLE_API_KEY', None)
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True

def get_material_rates_context():
    """
    Fetches current material rates from the database to provide context for AI.
    """
    try:
        from .models import MaterialRate
        rates = MaterialRate.objects.all()
        if not rates:
           return "No specific material rates found in database. Use standard Indian market rates."
        
        rates_str = "Current Local Material Rates:\n"
        for rate in rates:
            rates_str += f"- {rate.name}: ₹{rate.current_price} per {rate.unit}\n"
        return rates_str
    except Exception as e:
        return "Could not fetch local rates. Use standard Indian market rates."

def analyze_construction_image(image_path, material_type="Standard", square_footage=1000, floors=1):
    """
    AI-based construction cost estimation using image understanding.
    """

    # Ensure API Key is configured
    if not configure_genai():
        return {
            "error": "Google API Key is missing. Please configure it in settings or environment variables.",
            "estimated_cost": "N/A"
        }

    try:
        # Use a model that is definitely available
        model = genai.GenerativeModel("gemini-2.5-flash")
        image = PIL.Image.open(image_path)
        
        # Get live rates
        rates_context = get_material_rates_context()

        prompt = f"""
        You are an AI system trained to estimate construction and renovation costs in India.
        
        {rates_context}

        Project Details:
        - Image: Provided
        - Square Footage: {square_footage} sqft
        - Number of Floors: {floors} (Note: If analyzing a specific room, this may refer to the floor level or be irrelevant - trust the image context).
        - Material/Finish Type: {material_type}

        Analyze the given image to understand if it is a whole building, a specific room (kitchen, bedroom, bathroom), or a plot.

        CRITICAL VALIDATION STEP:
        Does this image depict a building, house, room, construction site, floor plan, or empty plot?
        - If NO (e.g., it's a person, animal, car, food, or random object): STOP immediately and return only: {{"error": "The image does not appear to be construction-related. Please upload a building, room, or plot image."}}
        - If YES: Proceed to estimate the cost.
        
        Task:
        1. Identify the scope: formatting the cost estimate for 'Whole House Construction' OR 'Interior/Room Renovation'.
        2. Estimate the cost based on the visible complexity, provided area, and local rates.
        
        Based on:
        1. The provided area ({square_footage} sqft) - critical for total cost.
        2. Visual complexity (luxury vs standard finishes).
        3. Local material rates provided above.
        
        Return ONLY valid JSON in the following format:
        {{
            "estimated_cost": "₹X,XX,XXX - ₹Y,YY,YYY",
            "reasoning": "Detected [Room Type/Building]. Estimated based on {square_footage} sqft. The design features...",
            "material_suggestion": "Suggested: {material_type} or similar suitable finish"
        }}
        """

        response = model.generate_content([prompt, image])

        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        # Log the full error to a file for debugging
        with open('ai_error.log', 'a') as f:
            import datetime
            f.write(f"{datetime.datetime.now()}: {str(e)}\n")
            
        return {
            "error": str(e),
            "estimated_cost": "Error"
        }

def get_chatbot_response(user_message):
    """
    Handles user queries using Gemini, with context about material rates.
    """
    if not configure_genai():
        return "I am currently offline. Please try again later. (API Key missing or invalid)"
        
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        rates_context = get_material_rates_context()
        
        system_prompt = f"""
        You are a helpful and professional virtual assistant for SmartBuild Construction Co. in India.
        Your goal is to clear user doubts regarding construction, material rates, and project estimates.
        
        {rates_context}
        
        Answer the user's questions clearly, concisely, and accurately based on the provided rates.
        If they ask about something not in the rates, give a general estimate and mention it's an approximation.
        Be polite and professional. Keep answers under 3-4 short paragraphs. Use markdown formatting if helpful (e.g., bolding, bullet points).
        """
        
        response = model.generate_content([system_prompt, user_message])
        return response.text
    except Exception as e:
        # Log error
        with open('ai_error.log', 'a') as f:
            import datetime
            f.write(f"{datetime.datetime.now()}: Chatbot Error - {str(e)}\n")
        return "I encountered an error processing your request. Please try again."
