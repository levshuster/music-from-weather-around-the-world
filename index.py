#!/usr/bin/env python3
'''
		orignally based on code from Jeff Ondich for CS251
		6 November 2020
'''
import argparse
from collections import namedtuple
from threading import Timer
from flask import Flask, make_response, request, jsonify, render_template
from pythonosc import udp_client
from datetime import datetime, timedelta
from dataclasses import dataclass

app = Flask(__name__)
ip = "localhost"
TIMEOUT = 30
musicport = 8000
players = []
client = udp_client.SimpleUDPClient(ip, musicport)

# create a named tuple called player with a checking time, BMP, and note values

@dataclass
class Player:
    check_in_time: datetime
    BPM: int
    note_values: list
    vote: int

# def send_message():

# 		client = udp_client.SimpleUDPClient(ip, musicport)
# 		client.send_message("/temperature", data["temperature_2m_mean"][i])
# 		client.send_message("/rain", data["rain_sum"][i])
# 		client.send_message("/snow", data["snowfall_sum"][i])
# 		client.send_message("/wind", data["windspeed_10m_max"][i])
# 		client.send_message("/tempo", tempo)

# ---- HELPER FUNCTIONS ----

def send_new_BPM():
	BPM_sum = 0
	for player in players:
		BPM_sum += player.BPM
		
	BPM = BPM_sum / len(players)
	print(BPM)

def tally_vote():
	votes = 0
	for player in players:
		votes += player.vote
	if votes >= len(players) / 2:
		for player in players:
			player.vote = 0
		print("Vote passed")
	else:
		print("Vote failed")

# --- ROUTES ---

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/new_player')
def get_user_number():
	current_timestamp = datetime.now()
	for index, player in enumerate(players):
		print("current time is " + str(current_timestamp))
		print("player time is " + str(player.check_in_time))
		if current_timestamp - player.check_in_time > timedelta(seconds=TIMEOUT):
			player.check_in_time = current_timestamp
			print("Player " + str(index) + " timed out and was replaced by a new user")
			return make_response(str(index))
	
	index = len(players)
	notes = [] # TODO: read notes from file
	players.append(Player(current_timestamp, 0, notes, 0))
	return make_response(str(index))

@app.route('/vote', methods=["POST"])
def receiveVote():
	response = request.json
	if response is None:
		return jsonify({'success': False})
		
	user_number = int(response['user_number'])
	
	players[user_number].vote = 1
	tally_vote()
	return jsonify({'success': True})

@app.route('/ping', methods=["POST"])
def receiveping():
	response = request.json
	if response is None:
		return jsonify({'success': False})
	
	user_number = int(response['user_number'])
	
	players[user_number].check_in_time = datetime.now()
	print("Player " + str(user_number) + " pinged")
	return jsonify({'success': True})

@app.route('/BPM', methods=["POST"])
def receiveBPM():
	response = request.json
	if response is None:
		return jsonify({'success': False})
	
	user_number = int(response['user_number'])
	BPM = int(response['BPM'])
	
	players[user_number].BPM = BPM
	send_new_BPM()

	return jsonify({'success': True})

@app.route('/playNote', methods=["POST"])
def receiveNote():
	response = request.json
	if response is None:
		return jsonify({'success': False})
	
	user_number = int(response['user_number'])
	note_length = int(response['note_length'])
	panning_value = int(response['panning_value'])
	note_number = int(response['note_number'])
	
	print(user_number)
	print(note_length)
	print(panning_value)
	print(note_number)
	
	return jsonify({'success': True})

if __name__ == '__main__':
	parser = argparse.ArgumentParser('A server to allow an arbitrary number of people to each control different parts of the same Max instrument')
	parser.add_argument('host', help='the host on which this application is running')
	parser.add_argument('port', type=int, help='the port on which this application is listening')
	arguments = parser.parse_args()
	app.run(host=arguments.host, port=arguments.port, debug=True)