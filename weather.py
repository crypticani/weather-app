import argparse
import json
import sys
import style
from configparser import ConfigParser
from urllib import parse, request, error


BASE_WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"

# Weather Condition Codes
# https://www.weatherapi.com/docs/weather_conditions.json
SUNNY = 1000
CLOUDY = [1003, 1006, 1009]
RAIN = [1063, 1180, 1183, 1186, 1189, 1192, 1195, 1198, 1201, 1240, 1243, 1246, 1249]
ATMOSPHERE = [1030, 1135, 1147]
SNOW = [1066, 1069, 1114, 1204, 1207, 1210, 1213, 1216, 1219, 1222, 1225, 1237, 1252, 1255, 1258, 1261, 1264]
DRIZZLE = [1072, 1150, 1153, 1168, 1171]
THUNDERSTORM = [1087, 1273, 1276, 1279, 1282]


def _get_api_key():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "secrets.ini" with structure:
        [weatherapi]
        api_key=<YOUR-OPENWEATHER-API-KEY>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["weatherapi"]["api_key"]


def read_user_cli_args():
    """Handles the CLI user interactions.
    Returns:
        argparse.Namespace: Populated namespace object
    """

    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )

    parser.add_argument(
        "city", nargs="+", type=str, help="enter the city name"
    )

    return parser.parse_args()


def build_weather_query(city_input):
    """Builds the URL for an API request to OpenWeather's weather API.
    Args:
        city_input (List[str]): Name of a city as collected by argparse
    Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    url = (
        f"{BASE_WEATHER_API_URL}"
        f"?key={api_key}&q={city_name}"
    )
    # url = BASE_WEATHER_API_URL + "?key="+api_key+"&q="+city_name
    return url


def get_weather_data(query_url):
    try:
        response = request.urlopen(query_url)
    except error.HTTPError:
        if error.http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif error.http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({error.http_error.code})")
    
    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_weather_info(weather_data):
    """Prints formatted weather information about a city.
    Args:
        weather_data (dict): API response from OpenWeather by city name
    """
    city = weather_data["location"]["name"]
    region = weather_data["location"]["name"]
    condition = weather_data["current"]["condition"]["text"]
    temperature = weather_data["current"]["temp_c"]

    weather_id = weather_data["current"]["condition"]["code"]

    style.change_color(style.REVERSE)
    print(f"{city} ({region})", end="")
    style.change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)
    style.change_color(color)
    print(f"\t{weather_symbol}", end=" ")
    print(
        f"{condition.capitalize():^{style.PADDING}}",
        end=" ",
    )

    style.change_color(style.RESET)
    print(f"({temperature}°{'C'})")


def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_params = ("💥", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("💧", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("💦", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("⛄️", style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("🌀", style.BLUE)
    elif weather_id in SUNNY:
        display_params = ("🔆", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("💨", style.WHITE)
    else:  # In case the API adds new weather codes
        display_params = ("🌈", style.RESET)
    return display_params


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data)
