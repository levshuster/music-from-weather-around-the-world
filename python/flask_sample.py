# python3 flask_sample.py localhost 5000
#!/usr/bin/env python3
'''
    template_sample.py
    Jeff Ondich
    6 November 2020

    Using templates in Flask.
'''
import sys
import argparse
import threading

from flask import Flask, request, jsonify
from pythonosc import udp_client

import flask
import json

app = flask.Flask(__name__)
ip = "localhost"
port = 8000
tempo = 60
starting = True
message_count=0
current_message = 0
i = 0

def send_message():
    global data
    global port
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
      print(data["windspeed_10m_max"][i])
      # print(tempo)

      client = udp_client.SimpleUDPClient(ip, port)
      client.send_message("/temperature", data["temperature_2m_mean"][i])
      client.send_message("/rain", data["rain_sum"][i])
      client.send_message("/snow", data["snowfall_sum"][i])
      client.send_message("/wind", data["windspeed_10m_max"][i])
      client.send_message("/tempo", tempo)

      i+=1
      # Schedule the next message to be sent in 20ms
      threading.Timer(60 / tempo, send_message).start()


@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/metaData', methods=["POST"])
def receiveMetaData():
  response = request.json
  global ip 
  ip = response['ip']
  global tempo 
  tempo = int(response['tempo'])
  print(tempo)
  global port 
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
    parser = argparse.ArgumentParser('A server to connect google maps --> Historical Weather Data --> Max')
    parser.add_argument('host', help='the host on which this application is running')
    parser.add_argument('port', type=int, help='the port on which this application is listening')
    arguments = parser.parse_args()
    app.run(host=arguments.host, port=arguments.port, debug=True)