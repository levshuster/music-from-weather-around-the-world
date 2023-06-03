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
import socket

app = Flask(__name__)
	
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

musicport = 8000
client = udp_client.SimpleUDPClient(ip, musicport)


TIMEOUT = 30
players = []
# client = udp_client.SimpleUDPClient(ip, musicport)

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

def get_new_notes():
	return []

def send_new_BPM():
	BPM_sum = 0
	player_not_at_default = 0
	for player in players:
		BPM_sum += player.BPM
		if player.BPM != 0:
			player_not_at_default += 1

	BPM = BPM_sum / len(players)
	client.send_message("/tempo", BPM)
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
	notes = get_new_notes() # TODO: read notes from file
	players.append(Player(current_timestamp, 0, notes, 0))
	client.send_message("/user_count", len(players))
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
	note_length = str(response['note_length'])
	panning_value = str(response['panning_value'])
	note_number = int(response['note_number'])
	

	notes = players[user_number].note_values
	note, ratio = notes[note_number]
	str1 = " "

	client.send_message("/user_count", str1.join([note_length, note, ratio, panning_value]))

	
	
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
	print("\n\nConnect to the instrument by being on the same nework on the host computer and going to http://" + ip + ":" + str(arguments.port)+ "\n\n")
	app.run(host="0.0.0.0", port=arguments.port, debug=True)
