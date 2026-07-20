from flask import Flask, redirect, render_template, request
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Sample2WeatherApp/1.0 (contact: example@example.com)",
    "Accept": "application/geo+json",
}


def weather_icon_from_description(description: str) -> str:
    text = description.lower()
    if any(word in text for word in ["sun", "clear"]):
        return "☀️"
    if any(word in text for word in ["cloud", "overcast"]):
        return "☁️"
    if any(word in text for word in ["rain", "showers", "drizzle"]):
        return "🌦️"
    if any(word in text for word in ["snow", "ice"]):
        return "❄️"
    if any(word in text for word in ["fog", "mist"]):
        return "🌫️"
    if any(word in text for word in ["storm", "thunder"]):
        return "⛈️"
    return "🌈"


def get_city_coordinates(city_name: str):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city_name, "format": "jsonv2", "limit": 1},
        headers={"User-Agent": "Sample2WeatherApp/1.0"},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not data:
        raise RuntimeError(f"Could not find coordinates for {city_name}.")

    return float(data[0]["lat"]), float(data[0]["lon"])


def get_weather(city_name: str):
    lat, lon = get_city_coordinates(city_name)
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    points_response = requests.get(points_url, headers=HEADERS, timeout=20)
    if points_response.status_code == 404:
        raise RuntimeError(f"The National Weather Service API does not provide coverage for {city_name}.")
    points_response.raise_for_status()
    points_data = points_response.json()

    forecast_url = points_data.get("properties", {}).get("forecast")
    if not forecast_url:
        raise RuntimeError("The NWS API did not return a forecast URL for that location.")

    forecast_response = requests.get(forecast_url, headers=HEADERS, timeout=20)
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()

    periods = forecast_data.get("properties", {}).get("periods", [])
    if not periods:
        raise RuntimeError("The NWS forecast response did not contain any periods.")

    period = periods[0]
    description = period.get("shortForecast", "No description available")

    return {
        "city": city_name,
        "country": "",
        "temperature": period.get("temperature"),
        "description": description,
        "humidity": None,
        "feels_like": period.get("temperature"),
        "icon_code": "nws",
        "icon_emoji": weather_icon_from_description(description),
        "icon_url": period.get("icon"),
    }


@app.get("/")
def index():
    return redirect("/weather")


@app.get("/weather")
def weather_page():
    return render_template("index.html", weather=None, error=None)


@app.post("/weather")
def weather():
    city_name = request.form.get("city", "").strip()
    if not city_name:
        return render_template("index.html", weather=None, error="Please enter a city name."), 400

    try:
        weather_data = get_weather(city_name)
    except requests.RequestException as exc:
        return render_template(
            "index.html",
            weather=None,
            error=f"Could not fetch weather for {city_name}: {exc}",
        ), 400
    except RuntimeError as exc:
        return render_template("index.html", weather=None, error=str(exc)), 400

    return render_template("index.html", weather=weather_data, error=None)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
