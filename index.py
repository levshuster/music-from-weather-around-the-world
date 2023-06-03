#!/usr/bin/env python3
'''
		orignally based on code from Jeff Ondich for CS251
		6 November 2020
'''
import argparse
from collections import namedtuple
from math import ceil
import random
from threading import Timer
from flask import Flask, make_response, request, jsonify, render_template
from pythonosc import udp_client
from datetime import datetime, timedelta
from dataclasses import dataclass
import socket

# --- READ DATA ---

def read_text_file(file_path) -> list:
    with open(file_path, 'r') as file:
        lines = file.readlines()
        array_2d = [line.strip().split(' ') for line in lines]
    return array_2d

file_path = 'PentatonicMinorScales.txt'  # Replace with the actual file path
pent_minor_scales = read_text_file(file_path)
active_scale = pent_minor_scales[random.randint(0, len(pent_minor_scales)-1)]

# --- FLASK ---

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
	number_of_notes_in_use = float(len(players)*2+2)
	number_of_notes_in_octive = float(len(active_scale))
	number_of_octives_in_use = ceil(number_of_notes_in_use / number_of_notes_in_octive)
	print("number of octives in use: " + str(number_of_octives_in_use))
	print("number of notes in use: " + str(number_of_notes_in_use))
	print("number_of_octives_in_use: " + str(number_of_octives_in_use))
	
	all_notes = []
	for i in range(number_of_octives_in_use) if number_of_octives_in_use > 1 else [1]:
		for note in active_scale:
			all_notes.append(str(note) + str(i+1))
	
	used_notes = []
	for player in players:
		for note in player.note_values:
			used_notes.append(note[0])
	# print("all notes: " + str(all_notes))
	print("used notes: " + str(used_notes))
	
	unused_notes = [x for x in all_notes if x not in used_notes]
	print("unused notes: " + str(unused_notes))

	return [
			[
				unused_notes[random.randint(0, len(unused_notes)-1)],
				2
			], [
				unused_notes[random.randint(0, len(unused_notes)-1)],
				2
			]
		]

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
	global active_scale
	votes = 0
	for player in players:
		votes += player.vote
	if votes >= len(players) / 2:
		for player in players:
			player.vote = 0
		old_scale = active_scale
		while active_scale == old_scale:
			active_scale = pent_minor_scales[random.randint(0, len(pent_minor_scales)-1)]
		print("new scale is " + str(active_scale))
		for player in players:
			player.notes = get_new_notes()
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
	notes = get_new_notes()
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

	client.send_message("/user_count", str1.join([note_length, str(note), str(ratio), panning_value]))

	
	
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
