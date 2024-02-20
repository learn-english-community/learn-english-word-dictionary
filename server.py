from flask import Flask, jsonify, request
from wiktionaryparser import WiktionaryParser
import requests
import urllib.request
from bs4 import BeautifulSoup
from constants import *
import consulate
import threading
import time

SERVER_PORT = 8081
APP_NAME = "word-wiktionary"
CONSUL_PORT = 8500
SERVER_IP = "localhost"
parser = WiktionaryParser()

# Register microservice to Consul agent
consul = consulate.Consul()
consul.agent.service.register(APP_NAME, port=SERVER_PORT, tags=['master'], ttl='10s')


def send_consul_heartbeat(ip: str, port: int):
  """Heartbeat for keeping the service alive"""
  while True:
    # Make a PUT request to update TTL
    try:
      response = requests.put(f'http://{ip}:{port}/v1/agent/check/pass/service:{APP_NAME}')

      if response.status_code != 200:
        print(f"Failed to send heartbeat: {response.text}")
    except Exception as e:
      print(f"Error sending heartbeat: {str(e)}")

    time.sleep(5)  # Send heartbeat every 5 seconds


# Start heartbeat thread
heartbeat_thread = threading.Thread(target=send_consul_heartbeat, args=(SERVER_IP, CONSUL_PORT), daemon=True)
heartbeat_thread.start()


def fetch_word(word):
  parsed = parser.fetch(word)[0]
  parsed["word"] = word
  return jsonify(parsed)


def server():
  app = Flask(__name__)

  @app.errorhandler(Exception)
  def http_error_handler(error):
    return jsonify({
      "error": "Bad request"
    }), 400

  @app.route('/define')
  def define():
    word = request.args.get('word')
    if len(word) == 0:
      return jsonify({
          "error": "Invalid word"
      }), 404

    return fetch_word(word)

  @app.route('/random')
  def random():
    soup = BeautifulSoup(urllib.request.urlopen(URL_RANDOM_ENGLISH))
    word = soup.title.string.split(' ')[0]

    return fetch_word(word)

  return app


app = server()
if __name__ == "__main__":
  app.run(port=SERVER_PORT)
