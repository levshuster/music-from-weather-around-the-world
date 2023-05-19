# music-from-weather-around-the-world

## Stack

- Python flask backend serves web dashboard
- Web dashboard calls Google Maps API to allow users to easily pick locations and explore street view
- Web dashboard calls OpenWeather API to fetch historical weather data
- Web dashboard pipes weather data into the python backend
- Python concurantly parses weather data and sends all the weather measures pertaining to each day on each beat via OSC protocol
- MAX Patch listens for OSC messages and generates music to represent the weather

## Installation

1. Clone repo or dowload zip file

```bash
git clone https://github.com/levshuster/music-from-weather-around-the-world.git
```

2. Start the server

navigate to the directory and run the following commands

```bash
python3 -m pip install -r requirements.txt
python3 index.py localhost 5000
```

3. Open the web dashboard by going to http://localhost:5000 in a web browser.
  - Ensure the IP address box matches your devices IP. If necacary update value to match
  - Set tempo, start date, and end date

4. Open Max

  - Install CNMAT externals from the MAX Package Manager then restart Max
  - Open `LEVANDHUGH_WEATHERSONIFICATION.maxpat`
  - Update the port number if necacary

5. Click on the map to fetch historical weather data and pipe it into our autmosphere generator.

  - Explore contrasting climate regions
  - What for oboe to stop playing before selecting the next location to avoid syncopation
  - Both listen and visually explore a locaiton with street view
  - Try different times of years or similar times across different years


## Code Exerpts From

- Google Maps API Documentation
- ChatGPT/Git-Copilot 
- Carleton College CS251 starter code written by Jeff Ondich


## Roalty Free Atmospheric Sound From
- videvo.net
- freesfx.co.uk