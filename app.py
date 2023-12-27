from config import API_KEY
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests

# Initialise the Flask application
app = Flask(__name__)
bootstrap = Bootstrap(app)

# Function to get the coordinates for a given city
def get_coordinates(city_name, api_key="your_api_key"):

    # API endpoint for searching cities
    api_url = "https://api.opentripmap.com/0.1/en/places/geoname"

    # Parameters to pass to the API
    params = {
        "name": city_name,
        "apikey": api_key,
        "format": "json",
        "lang": "en"
    }

    # Send a request to the API endpoint
    response = requests.get(api_url, params=params)

    # If the response was successful, process it and return the coordinates
    if response.status_code == 200:
        city_info = response.json()

        # Print the response for debugging
        print("City details:")
        print(city_info)
        
        # Retrieve the latitude and longitude from the response
        lat = city_info.get("lat", "N/A")
        lon = city_info.get("lon", "N/A")

        return lat, lon
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

# Function to get the landmarks for a given city
def get_landmarks(latitude, longitude, radius=1000, category="interesting_places", min_rating="3h", api_key="your_api_key"):

    # API endpoint for searching landmarks
    api_url = "https://api.opentripmap.com/0.1/en/places/radius"

    # Parameters to pass to the API
    params = {
        "lang": "en",
        "radius": radius,
        "lat": latitude,
        "lon": longitude,
        "kinds": category,
        "format": "json",
        "apikey": api_key,
        "rate": min_rating,
        "limit": 300
    }

    response = requests.get(api_url, params=params)

    # If the response was successful, process it and return the landmarks
    if response.status_code == 200:
        landmarks = response.json()

        print("Landmarks: ")
        print(landmarks)
        landmarks = filter_landmarks(landmarks)

        return landmarks
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None

# Function to filter out duplicate landmarks
def filter_landmarks(city_landmarks):
    unique_names = set()

    for landmark in city_landmarks:
        name = landmark.get("name", "N/A")
        kinds = landmark.get("kinds", "N/A")
        rate = landmark.get("rate", "N/A")
        xid = landmark.get("xid", "N/A")

        # Check if the name is unique, if not, skip printing
        if name in unique_names:
            city_landmarks.remove(landmark)
            continue

        unique_names.add(name)

        # Print landmark details for debugging
        print(f"Landmark: {name} | Category: {kinds} | Rating: {rate} | ID: {xid}")
    
    # Convert the set back to a list
    return city_landmarks

# Define the index route
@app.route('/')
def index():
    app.logger.debug("Rendering index.html")
    return render_template('index.html')

# Define the route to handle the form submission
@app.route('/landmarks', methods=['POST'])
def explore_landmarks():
    city = request.form.get('city')
    app.logger.debug(f"Received POST request with city: {city}")
    api_key = API_KEY

    # Get coordinates for the city
    latitude, longitude = get_coordinates(city, api_key=api_key)

    # If the coordinates were found, get the landmarks
    if latitude is not None and longitude is not None:
        
        # Get landmarks for the city
        min_rating_to_search = "3"
        city_landmarks = get_landmarks(latitude, longitude, api_key=api_key, min_rating=min_rating_to_search)
        return render_template('results.html', landmarks=city_landmarks, city=city)
    else:
        return render_template('results.html', landmarks=[], city="")

# Run the app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500, debug=True)
