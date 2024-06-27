import requests
import json
import os
import sqlalchemy as db
import pandas as pd 

def fetch_nearby_places(api_key, location, radius, place_type, keyword):
    
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Define the parameters
    params = {
        'location': location,  # 'latitude,longitude'
        'radius': radius,  #meters
        'type': place_type,
        'keyword': keyword,
        'key': api_key
    }
    
    # Make the request
    response = requests.get(endpoint_url, params=params)
    
    if response.status_code == 200:
        # Parse the response JSON
        places = response.json()
        return places
    else:
        return None

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    
    api_key = os.getenv('google_maps_key')
    
    # Location, radius, type, and keyword for the search
    location = '40.706839018110415, -74.01084140000002'
    radius = 1609
    place_type = 'library'
    keyword = 'study'

    places_data = fetch_nearby_places(api_key, location, radius, place_type, keyword)


    if places_data:
        # Save the data to a JSON file
        save_to_json(places_data, 'nearby_places.json')
        print("Nearby places data has been saved to 'nearby_places.json'")

        df = pd.json_normalize(places_data['results'])
        
        # Extract only the required columns
        df = df[['name', 'geometry.location.lat', 'geometry.location.lng', 'opening_hours.open_now', 'vicinity']]
        
        # Rename columns to match desired database schema
        df.rename(columns={
            'geometry.location.lat': 'latitude',
            'geometry.location.lng': 'longitude',
            'opening_hours.open_now': 'open_now'
        }, inplace=True)

        # Create an SQLite database engine
        engine = db.create_engine('sqlite:///locations.db')

        # Create a table and insert the data into the SQLite database
        df.to_sql('locations', con=engine, if_exists='replace', index=False)

        with engine.connect() as connection:
            query_result = connection.execute(db.text("SELECT * FROM locations;")).fetchall()
            print(pd.DataFrame(query_result))
    else:
        print("Failed to retrieve data from the Google Maps API")
    
    


    

