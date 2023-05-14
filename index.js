const maxApi = require("max-api");
// keeps the first async fucntion from continuing once the second async function is created
run_number = 0;





// OSC

async function sendOSC(weatherData, ip, port, callNumber) {
	console.log(weatherData);
	const numberOfDays = weatherData.rain_sum.length;
	// const startingTime = Date.now();
	// const millisecondsPerBeat = 60000 / document.getElementById("tempo-input").value;
	for (var i = 0; i < numberOfDays; i++) {
		if (callNumber != run_number) break;
		rainSum = weatherData.rain_sum[i];
		snowfallSum = weatherData.snowfall_sum[i];
		temperature2mMean = weatherData.temperature_2m_mean[i];
		time = weatherData.time[i];
		windspeed10mMax = weatherData.windspeed_10m_max[i];
		
		if (time == "2023-05-05") {
			alert("This project is based on historical data, please select an earlier date.");
			break;
		}
		
		maxApi.outlet(rainSum, snowfallSum, temperature2mMean, time, windspeed10mMax)

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

// WEATHER

async function getWeatherData(lat, lng) {
	// const start_date = "2022-12-04";
	const start_date = document.getElementById("start-date-picker").value
	// const end_date = "2023-04-27";
	const end_date = document.getElementById("end-date-picker").value
	const daily = "temperature_2m_mean,rain_sum,snowfall_sum,windspeed_10m_max";
	const timezone = "America/New_York";
	const url = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lng}&start_date=${start_date}&end_date=${end_date}&daily=${daily}&timezone=${timezone}`;
	const response = await fetch(url);
	const data = await response.json();
	
	run_number += 1;
	return data;
}

// MAP

async function initMap() {
	document.getElementById('ip-input').value = await getIPFromIpify();
	
	const myLatlng = { lat: 44.45677677613184, lng: -93.15629227226407};
	const map = new google.maps.Map(document.getElementById("map"), {
		zoom: 4,
		center: myLatlng,
	});
	let infoWindow = new google.maps.InfoWindow({
		content: "Click the map to get Lat/Lng!",
		position: myLatlng,
	});
	infoWindow.open(map);
	
	map.addListener("click", async (mapsMouseEvent) => {
		infoWindow.close();
		infoWindow = new google.maps.InfoWindow({
			position: mapsMouseEvent.latLng,
		});

		lat = mapsMouseEvent.latLng.toJSON().lat;
		lng = mapsMouseEvent.latLng.toJSON().lng;
		infoWindow.setContent(
			`(${lat.toFixed(2)}, ${lng.toFixed(2)})`
		);
		
		const weatherData = await getWeatherData(
			lat,lng
		);
		await sendOSC(
			weatherData.daily,
			document.getElementById("ip-input").value,
			document.getElementById("port-input").value,
			run_number
		);
		infoWindow.open(map);
	});
}

// HELPERS

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

function getIPFromIpify() {
	return new Promise((resolve, reject) => {
	  fetch('https://api.ipify.org?format=json')
		.then(response => response.json())
		.then(data => resolve(data.ip))
		.catch(error => reject(error))
	});
}

const tempoInput = document.getElementById('tempo-input');
const tempoValue = document.getElementById('tempo-value');

function updateTempoValue() {
	const currentTempo = tempoInput.value;
	tempoValue.textContent = currentTempo;
}

tempoInput.addEventListener('input', updateTempoValue);
tempoValue.addEventListener('input', () => {
	const currentTempo = tempoValue.textContent;
	tempoInput.value = currentTempo;
});


// MAIN

window.initMap = initMap;
updateTempoValue();
