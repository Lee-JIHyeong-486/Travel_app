from dotenv import load_dotenv
import os

# Load .env file from current directory or specify path
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FOURSQUARE_API_KEY = os.getenv('FOURSQUARE_API_KEY')
OPENROUTESERVICE_API_KEY = os.getenv('OPENROUTESERVICE_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")