# I WAS IN HURRY, SO THE CODE HAS MANY BUGS TO FIX, FEEL FREE TO COMMIT FIXED SOLUTIONS OF BUGS.
# CODE CREATED BY t.me/anonimidin.
import os
import logging
import random
import requests
import json
from datetime import date, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext

# Load environment variables from a .env file
load_dotenv()
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Check if API tokens are present
if BOT_API_TOKEN is None or NASA_API_KEY is None:
    raise ValueError("API tokens not found in env var.")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Telegram bot instance and dispatcher
bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher(bot)

# Get the directory of the current script, idk why i couldn't read from directly planets.json
script_directory = os.path.dirname(os.path.abspath(__file__))
planets_json_path = os.path.join(script_directory, "planets.json")
# Open 'planets.json' with 'utf-8' encoding
with open(planets_json_path, "r", encoding="utf-8") as planets_file:
    planets_data = json.load(planets_file)


# Constants for button labels
PLANETS_BUTTON = "🪐 Planets"
SPACE_NEWS_BUTTON = "🌌 Space News"
SPACE_FACT_BUTTON = "🚀 Space Fact"
APOD_BUTTON = "🔭 Astronomy Picture of the Day"
MARS_WEATHER_BUTTON = "🌦 Mars Weather"
NEAR_EARTH_ASTEROIDS_BUTTON = "🌠 Near-Earth Asteroids"
ISS_LOCATION_BUTTON = "🛰️ ISS Location"


# Function to fetch astronomy news
def fetch_astronomy_news():
    url = "https://www.nasa.gov/news-release/feed/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        news_items = []
        for item in items[:5]:
            title = item.find("title").text
            link = item.find("link").text
            description = item.find("description").text
            news_items.append(f'🚀 <a href="{link}">{title}</a>\n{description}\n')
        return "\n".join(news_items)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching astronomy news: {e}")
        return "An error occurred while fetching astronomy news."


# Function to fetch Astronomy Picture of the Day (APOD)
def fetch_apod():
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": NASA_API_KEY,
        "hd": True,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("title"), data.get("url"), data.get("explanation")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching APOD data: {e}")
        return None, None, None


# Function to ouput user randomly space facts from facts.txt
def generate_space_fact():
    try:
        with open("facts.txt", "r", encoding="utf-8") as file:
            facts = file.readlines()
            fact = random.choice(facts).strip()
            return fact
    except Exception as e:
        logging.error(f"Error fetching space fact: {e}")
        return "An error occurred while fetching a space fact."


# Function to fetch near-Earth asteroids data
def fetch_near_earth_asteroids():
    try:
        today = date.today()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        asteroid_count = data["element_count"]

        if asteroid_count == 0:
            return "🌠 No near-Earth asteroids are currently known."

        closest_approach_date = data["near_earth_objects"][start_date][0][
            "close_approach_data"
        ][0]["close_approach_date_full"]
        estimated_diameter = data["near_earth_objects"][start_date][0][
            "estimated_diameter"
        ]["kilometers"]["estimated_diameter_max"]

        return (
            f"🔭 There are {asteroid_count} near-Earth asteroids currently known.\n\n"
            f"🌠 The closest asteroid will approach Earth on {closest_approach_date} and its estimated diameter is approximately {estimated_diameter} kilometers."
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching near-Earth asteroids data: {e}")
        return "An error occurred while fetching near-Earth asteroids data."

"""THIS FUNC IS NOT WORKING CORRECTLY (MAYBE)"""
# Function to fetch Mars weather
async def fetch_mars_weather():
    api_url = f"https://api.nasa.gov/insight_weather/?api_key={NASA_API_KEY}&feedtype=json&ver=1.0"
    try:
        response = await bot.session.get(api_url)
        response.raise_for_status()
        data = await response.json()

        if not data.get("sol_keys"):
            return "No Mars weather data available at the moment. Please check again later."

        latest_sol = max(data["sol_keys"])
        temperature = data[latest_sol]["AT"]["av"]
        wind_speed = data[latest_sol]["HWS"]["av"]

        message = (
            f"🌡 Mars Weather:\n"
            f"🌡 Temperature: {temperature} °C\n"
            f"💨 Wind Speed: {wind_speed} m/s"
        )
        return message
    except Exception as e:
        logging.error(f"Error fetching Mars weather data: {e}")
        return "An error occurred while fetching Mars weather data."
"""THIS FUNC IS NOT WORKING CORRECTLY"""

# Function to fetch ISS location and astronaut information
def fetch_iss_data():
    try:
        # Fetch ISS location
        iss_url = "http://api.open-notify.org/iss-now.json"
        iss_response = requests.get(iss_url)
        iss_response.raise_for_status()
        iss_data = iss_response.json()

        # Fetch astronaut information
        astronauts_url = "http://api.open-notify.org/astros.json"
        astronauts_response = requests.get(astronauts_url)
        astronauts_response.raise_for_status()
        astronauts_data = astronauts_response.json()

        # Extract ISS location data
        iss_latitude = iss_data.get("iss_position", {}).get("latitude", "N/A")
        iss_longitude = iss_data.get("iss_position", {}).get("longitude", "N/A")

        # Extract astronaut information and create hyperlinks
        astronauts = astronauts_data.get("people", [])
        astronaut_info = "\n".join(
            [
                f"• [{astronaut['name']}](https://en.wikipedia.org/wiki/{astronaut['name']}) on [{astronaut['craft']}](https://en.wikipedia.org/wiki/{astronaut['craft']})"
                for astronaut in astronauts
            ]
        )

        # Create the combined message
        message = (
            f"""
            🛰️ The ISS: The International Space Station is a space station located in low Earth orbit. It is a multinational collaborative project involving space agencies such as NASA (United States), Roscosmos (Russia), ESA (European Space Agency), JAXA (Japan Aerospace Exploration Agency), and CSA (Canadian Space Agency). It serves as a platform for scientific research, technological development, and international cooperation in space exploration.\nThe ISS orbits the Earth approximately every 90 minutes, providing a unique vantage point for scientific experiments and observations of our planet. It is a symbol of international cooperation in space exploration and continues to play a crucial role in advancing our understanding of life in space and conducting research in microgravity environments.\n"""
            f"\n🛰️ Current Location:\n"
            f"• Latitude: {iss_latitude}\n"
            f"• Longitude: {iss_longitude}\n\n"
            f"🚀 Astronauts on board:\n{astronaut_info}"
        )
        return message
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching ISS data: {e}")
        return "An error occurred while fetching ISS data."


# Start command handler
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    planets_button = KeyboardButton(PLANETS_BUTTON)
    space_news_button = KeyboardButton(SPACE_NEWS_BUTTON)
    space_fact_button = KeyboardButton(SPACE_FACT_BUTTON)
    apod_button = KeyboardButton(APOD_BUTTON)
    mars_weather_button = KeyboardButton(MARS_WEATHER_BUTTON)
    near_earth_asteroids_button = KeyboardButton(NEAR_EARTH_ASTEROIDS_BUTTON)
    iss_location_button = KeyboardButton(ISS_LOCATION_BUTTON)

    markup.add(
        planets_button,
        space_news_button,
        space_fact_button,
        apod_button,
        mars_weather_button,
        near_earth_asteroids_button,
        iss_location_button,
    )

    await message.answer(
        "Welcome to the Solar System Information Bot (COSMIX)! Choose an option:",
        reply_markup=markup,
    )


# Mars weather button handler
@dp.message_handler(lambda message: message.text.lower() == MARS_WEATHER_BUTTON.lower())
async def show_mars_weather(message: types.Message, state: FSMContext):
    mars_weather = await fetch_mars_weather()
    await message.answer(mars_weather, parse_mode=ParseMode.MARKDOWN)


# Planets button handler
@dp.message_handler(lambda message: message.text.lower() == PLANETS_BUTTON.lower())
async def show_planets(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    planets = list(planets_data.keys())
    for planet in planets:
        markup.add(KeyboardButton(f"🪐 {planet}"))
    markup.add(KeyboardButton("↩️ Back"))
    await message.answer(
        "The Solar System consists of nine planets. Choose a planet to learn more or press '↩️ Back' to return to the main menu:",
        reply_markup=markup,
    )


"""THIS FUNC IS NOT WORKING CORRECTLY"""
# Message handler to listen for planet names
@dp.message_handler(lambda message: message.text.lower() in planets_data.keys())
async def handle_planet_name(message: types.Message):
    await show_planet_info(message)


# Show_planet_info function
async def show_planet_info(message: types.Message):
    planet_name = message.text.lower()
    if planet_name in planets_data:
        planet_info = planets_data[planet_name]
        planet_description = planet_info.get(
            "description", "Planet information not available."
        )

        response_message = f"🪐 {planet_name.capitalize()} Information:\n\n"
        response_message += f"Description: {planet_description}\n"

        await message.answer(response_message, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Planet information not available.")

"""THIS FUNC IS NOT WORKING CORRECTLY"""


# Back button handler
@dp.message_handler(lambda message: message.text.lower() == "↩️ back")
async def go_back_to_main_menu(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    planets_button = KeyboardButton(PLANETS_BUTTON)
    space_news_button = KeyboardButton(SPACE_NEWS_BUTTON)
    space_fact_button = KeyboardButton(SPACE_FACT_BUTTON)
    apod_button = KeyboardButton(APOD_BUTTON)
    mars_weather_button = KeyboardButton(MARS_WEATHER_BUTTON)
    near_earth_asteroids_button = KeyboardButton(NEAR_EARTH_ASTEROIDS_BUTTON)
    iss_location_button = KeyboardButton(ISS_LOCATION_BUTTON)

    markup.add(
        planets_button,
        space_news_button,
        space_fact_button,
        apod_button,
        mars_weather_button,
        near_earth_asteroids_button,
        iss_location_button,
    )

    await message.answer("Choose an option:", reply_markup=markup)


# Space news button handler
@dp.message_handler(lambda message: message.text.lower() == SPACE_NEWS_BUTTON.lower())
async def show_space_news(message: types.Message):
    news = fetch_astronomy_news()
    await message.answer(news, parse_mode=ParseMode.HTML)


# Astronomy Picture of the Day (APOD) button handler
@dp.message_handler(lambda message: message.text.lower() == APOD_BUTTON.lower())
async def show_apod(message: types.Message):
    title, image_url, explanation = fetch_apod()
    await message.answer(title)
    await message.answer_photo(photo=image_url, caption="", parse_mode=ParseMode.HTML)
    await message.answer(explanation, parse_mode=ParseMode.HTML)


# Space fact button handler
@dp.message_handler(lambda message: message.text.lower() == SPACE_FACT_BUTTON.lower())
async def show_space_fact(message: types.Message):
    space_fact = generate_space_fact()
    await message.answer(space_fact)


# Near-Earth Asteroids button handler
@dp.message_handler(
    lambda message: message.text.lower() == NEAR_EARTH_ASTEROIDS_BUTTON.lower()
)
async def show_near_earth_asteroids(message: types.Message):
    asteroid_info = fetch_near_earth_asteroids()
    await message.answer(asteroid_info)


# ISS Location button handler
@dp.message_handler(lambda message: message.text.lower() == ISS_LOCATION_BUTTON.lower())
async def show_iss_location(message: types.Message):
    iss_location = fetch_iss_data()
    await message.answer(iss_location, parse_mode=ParseMode.MARKDOWN)


# Main bot execution
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
