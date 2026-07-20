# Weather Flask App

A simple Flask web app that lets a user enter a city name and displays current weather information from the National Weather Service API.

## Features

- Search for weather by city name
- Display current temperature and weather condition
- Show a weather icon based on the returned condition
- Basic error handling for unsupported or invalid locations

## Requirements

- Python 3.10+
- Flask
- requests

## Setup

1. Open a terminal in this folder.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Run the app

From the project folder, run:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000/weather
```

## Notes

- The app uses the National Weather Service API via the public weather.gov endpoints.
- Coverage is strongest for U.S. locations.
- The app currently uses geocoding through Nominatim to resolve the city name to coordinates before requesting weather data.
