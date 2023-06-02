#!/usr/bin/env python3
'''
		orignally based on code from Jeff Ondich for CS251
		6 November 2020
'''
import argparse
from threading import Timer
from flask import Flask, request, jsonify, render_template
from pythonosc import udp_client

app = Flask(__name__)
ip = "localhost"
musicport = 8000
tempo = 60
starting = True
message_count=0
current_message = 0
i = 0

def send_message():
	global data
	global musicport
	global tempo
	global ip
	global message_count
	global current_message
	global i
	if message_count != current_message:
		current_message +=1
		i = 0
	if i != len(data['time']):
		
		# Code to send the message containing the data variable goes here
		# print(data["time"][i])
		# print(data["temperature_2m_mean"][i])
		# print(data["rain_sum"][i])
		# print(data["snowfall_sum"][i])
		# print(data["windspeed_10m_max"][i])
		# print(tempo)

		client = udp_client.SimpleUDPClient(ip, musicport)
		client.send_message("/temperature", data["temperature_2m_mean"][i])
		client.send_message("/rain", data["rain_sum"][i])
		client.send_message("/snow", data["snowfall_sum"][i])
		client.send_message("/wind", data["windspeed_10m_max"][i])
		client.send_message("/tempo", tempo)

		i+=1
		Timer(60 / tempo, send_message).start()


@app.route('/')
def home():
	return render_template('index.html')

@app.route('/metaData', methods=["POST"])
def receiveMetaData():
	response = request.json
	global ip 
	ip = response['ip']
	global tempo 
	tempo = int(response['tempo'])
	print(tempo)
	global musicport 
	port = int(response['port'])
	print(response)
	return {'ip': ip}, 200

@app.route('/weatherData', methods=['POST'])
def weatherData():
	global data 
	data= request.get_json()
	print(data)
	global starting 
	global message_count
	message_count += 1
	if starting:
		send_message()
	return jsonify({'success': True})


if __name__ == '__main__':
	parser = argparse.ArgumentParser('A server to allow an arbitrary number of people to each control different parts of the same Max instrument')
	parser.add_argument('host', help='the host on which this application is running')
	parser.add_argument('port', type=int, help='the port on which this application is listening')
	arguments = parser.parse_args()
	app.run(host=arguments.host, port=arguments.port, debug=True)