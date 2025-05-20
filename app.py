

# import os
# from flask import Flask, request, jsonify
# import requests
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv(dotenv_path='.env')

# app = Flask(__name__)

# # API Keys
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
# WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
# GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"

# @app.route('/generate-plan', methods=['POST'])
# def generate_plan():
#     try:
#         data = request.json
#         location = data.get("location", "Kandy").capitalize()
#         start_date = data.get("start_date", "2025-04-08")
#         duration = data.get("duration", "3 days")
#         budget = data.get("budget", "1000")
#         interests = data.get("interests", "history")
#         travel_style = data.get("travel_style", "budget")
#         accommodation = data.get("accommodation", "semi luxury")

#         # Fetch top attractions dynamically using Google Places API
#         places_url = (
#             f"https://maps.googleapis.com/maps/api/place/textsearch/json?"
#             f"query=top+attractions+in+{location}+Sri+Lanka&"
#             f"key={GOOGLE_PLACES_API_KEY}"
#         )
#         places_response = requests.get(places_url).json()

#         # Extract the names of the attractions
#         attractions = [place['name'] for place in places_response.get('results', [])[:5]]

#         # If no attractions are found, use a placeholder
#         if not attractions:
#             attractions = ["No attractions found for this location."]

#         # Fetch weather data dynamically
#         weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location},LK&appid={WEATHER_API_KEY}"
#         weather_response = requests.get(weather_url, timeout=10)
#         weather_data = weather_response.json()
#         current_weather = weather_data.get('weather', [{}])[0].get('description', 'Not available')

#         # Fetch travel tips using Google Custom Search Engine (CSE)
#         cse_query = f"travel tips for {location} Sri Lanka {interests} site-specific"
#         cse_url = f"{GOOGLE_CSE_URL}?key={GOOGLE_PLACES_API_KEY}&cx={GOOGLE_CSE_ID}&q={cse_query}"
#         cse_response = requests.get(cse_url).json()
#         cse_results = cse_response.get('items', [])[:3]
#         travel_tips = [item['snippet'] for item in cse_results] if cse_results else ["No additional tips found."]

#         # Prepare the prompt for Groq API to generate a travel plan
#         prompt = f"""
#         Generate a travel plan for {location}, Sri Lanka, starting on {start_date} for {duration}.
#         Budget: ${budget}
#         Interests: {interests}
#         Travel Style: {travel_style}
#         Accommodation Preference: {accommodation}
#         Top Attractions in {location}: {', '.join(attractions) if attractions else 'No attractions available'}
#         Current Weather: {current_weather}
#         Additional Travel Tips from Web (specific to {location}): {', '.join(travel_tips)}
#         Provide a day-wise itinerary with estimated costs and travel tips.
#         **Important**: Only include activities, attractions, and recommendations located within the city of {location}.
#         **Pricing Instructions**:
#         - Ensure total costs stay within ${budget} across {duration}.
#         - Include transportation, accommodation, meals, and attraction costs based on the available data.
#         - If costs are not available, clearly note that the costs are not specified.
#         """
        
#         # Call the Groq API with the dynamically generated prompt
#         response = requests.post(
#             GROQ_API_URL,
#             headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
#             json={
#                 "model": "llama-3.1-8b-instant",
#                 "messages": [
#                     {"role": "system", "content": "You are a helpful travel assistant."},
#                     {"role": "user", "content": prompt}
#                 ]
#             }
#         )

#         if response.status_code == 200:
#             travel_plan = response.json()['choices'][0]['message']['content']
#             return jsonify({"travel_plan": travel_plan})
#         else:
#             return jsonify({"error": "Failed to generate travel plan using Groq API."}), 500

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)







from flask_cors import CORS
import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='.env')

app = Flask(__name__)
CORS(app)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Unified key for CSE & Places
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"

@app.route('/', methods=['GET', 'POST'])
def generate_plan():
    if request.method == 'GET':
        return "Please send a POST request with JSON data."

    try:
        data = request.get_json()

        location = data.get("location", "Kandy").capitalize()
        start_date = data.get("start_date", "2025-04-08")
        duration = data.get("duration", "3 days")
        budget = data.get("budget", "1000")
        interests = data.get("interests", "history")
        travel_style = data.get("travel_style", "budget")
        accommodation = data.get("accommodation", "semi luxury")
        people_count = data.get("people_count", 1)

        # Fetch top attractions using Google Places API
        places_url = (
            f"https://maps.googleapis.com/maps/api/place/textsearch/json?"
            f"query=top+attractions+in+{location}+Sri+Lanka&"
            f"key={GOOGLE_API_KEY}"
        )
        places_response = requests.get(places_url).json()
        attractions = [place['name'] for place in places_response.get('results', [])[:5]]

        if not attractions:
            attractions = ["No attractions found for this location."]

        # Fetch weather data
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location},LK&appid={WEATHER_API_KEY}"
        weather_response = requests.get(weather_url, timeout=10)
        weather_data = weather_response.json()
        current_weather = weather_data.get('weather', [{}])[0].get('description', 'Not available')

        # Fetch travel tips using Google CSE
        cse_query = f"travel tips for {location} Sri Lanka {interests}"
        cse_url = f"{GOOGLE_CSE_URL}?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={cse_query}"
        cse_response = requests.get(cse_url).json()
        cse_results = cse_response.get('items', [])[:3]
        travel_tips = [item['snippet'] for item in cse_results] if cse_results else ["No additional tips found."]

        # Construct prompt for Groq API
        prompt = f"""
        Generate a travel plan for {location}, Sri Lanka, starting on {start_date} for {duration}.
        This plan is for {people_count} people.
        Total Budget: ${budget}
        Interests: {interests}
        Travel Style: {travel_style}
        Accommodation Preference: {accommodation}
        Top Attractions in {location}: {', '.join(attractions)}
        Current Weather: {current_weather}
        Additional Travel Tips from Web (specific to {location}): {', '.join(travel_tips)}
        
        Provide a day-wise itinerary with estimated costs and travel tips.

        **Important**: Only include activities, attractions, and recommendations located within the city of {location}.

        **Pricing Instructions**:
        - Ensure total costs stay within ${budget} for {people_count} people across {duration}.
        - Include transportation, accommodation, meals, and attraction costs based on the available data.
        - If costs are not available, clearly note that the costs are not specified.
        """

        # Call Groq API
        response = requests.post(
            GROQ_API_URL,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a helpful travel assistant."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code == 200:
            travel_plan = response.json()['choices'][0]['message']['content']
            return jsonify({"travel_plan": travel_plan})
        else:
            return jsonify({"error": "Failed to generate travel plan using Groq API."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
