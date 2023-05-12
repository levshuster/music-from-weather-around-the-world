// keeps the first async fucntion from continuing once the second async function is created
run_number = 0;
async function getWeatherData(lat, lng) {
    const start_date = "2022-12-04";
    const end_date = "2023-04-27";
    const daily = "temperature_2m_mean,rain_sum,snowfall_sum,windspeed_10m_max";
    const timezone = "America/New_York";
    const url = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lng}&start_date=${start_date}&end_date=${end_date}&daily=${daily}&timezone=${timezone}`;
  
    const response = await fetch(url);
    const data = await response.json();
    run_number += 1;
    return data;
  }
  
function sleepForABeat() {
    const millisecondsPerBeat = 60000 / document.getElementById("tempo-input").value; // Calculate the duration of one beat
    // console.log(new Date().toISOString().slice(14, -5));
    return new Promise(resolve => setTimeout(resolve, millisecondsPerBeat)); // Use setTimeout() to pause for one beat
}

function sleepUntil(timestamp) {
    const timeToSleep = timestamp - Date.now();
    if (timeToSleep <= 0) {
      return;
    }
    const timer = setTimeout(() => {}, timeToSleep);
    while (Date.now() < timestamp) {}
    clearTimeout(timer);
  }

async function sendOSC(weatherData, ip, callNumber) {
    console.log(weatherData);
    const numberOfDays = weatherData.rain_sum.length;
    const startingTime = Date.now();
    const millisecondsPerBeat = 60000 / document.getElementById("tempo-input").value;
    for (var i = 0; i < numberOfDays; i++) {
        if (callNumber != run_number) {
            break;
        }
        rainSum = weatherData.rain_sum[i];
        snowfallSum = weatherData.snowfall_sum[i];
        temperature2mMean = weatherData.temperature_2m_mean[i];
        time = weatherData.time[i];
        windspeed10mMax = weatherData.windspeed_10m_max[i];
        document.getElementById("time").textContent = time;
        document.getElementById("temperature").textContent = temperature2mMean;
        document.getElementById("rain").textContent = rainSum;
        document.getElementById("snowfall").textContent = snowfallSum;
        document.getElementById("windspeed").textContent = windspeed10mMax;
        await sleepForABeat();
        // console.log(new Date().toISOString().slice(14, -5));
        // sleepUntil(startingTime + millisecondsPerBeat * (i+1)); // TODO: check to see if i or i+1 is correct
    }
}
    
    

function initMap() {
    const myLatlng = { lat: -25.363, lng: 131.044 };
    const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,
    center: myLatlng,
    });
    // Create the initial InfoWindow.
    let infoWindow = new google.maps.InfoWindow({
    content: "Click the map to get Lat/Lng!",
    position: myLatlng,
    });

    infoWindow.open(map);
    // Configure the click listener.
    map.addListener("click", async (mapsMouseEvent) => {
    // Close the current InfoWindow.
    infoWindow.close();
    // Create a new InfoWindow.
    infoWindow = new google.maps.InfoWindow({
        position: mapsMouseEvent.latLng,
    });
    infoWindow.setContent(
        JSON.stringify(mapsMouseEvent.latLng.toJSON(), null, 2)
    );
    
    const weatherData = await getWeatherData(
        mapsMouseEvent.latLng.toJSON().lat,
        mapsMouseEvent.latLng.toJSON().lng
    );
    await sendOSC(
        weatherData.daily,
        document.getElementById("ip-input").value,
        run_number
    );
    // console.log(mapsMouseEvent.latLng.toJSON().lat);
    // console.log(mapsMouseEvent.latLng.toJSON().lng);
    // const ipAddress = document.getElementById("ip-input").value;
    // console.log(ipAddress);
    // const tempo = document.getElementById("tempo-input").value;
    // console.log(tempo);
    infoWindow.open(map);
    });
}
window.initMap = initMap;	