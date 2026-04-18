def get_chatbot_response(user_message):
    """
    Handles user queries using Gemini, with context about material rates.
    """
    if not configure_genai():
        return "I am currently offline. Please try again later."
        
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        rates_context = get_material_rates_context()
        
        system_prompt = f"""
        You are a helpful and professional virtual assistant for SmartBuild Construction Co. in India.
        Your goal is to clear user doubts regarding construction, material rates, and project estimates.
        
        {rates_context}
        
        Answer the user's questions clearly, concisely, and accurately based on the provided rates.
        If they ask about something not in the rates, give a general estimate and mention it's an approximation.
        Be polite and professional. Keep answers under 3-4 short paragraphs.
        """
        
        response = model.generate_content([system_prompt, user_message])
        return response.text
    except Exception as e:
        # Log error
        with open('ai_error.log', 'a') as f:
            import datetime
            f.write(f"{datetime.datetime.now()}: Chatbot Error - {str(e)}\n")
        return "I encountered an error processing your request. Please try again."
