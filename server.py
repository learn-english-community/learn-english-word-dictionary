from flask import Flask, jsonify, request
from wiktionaryparser import WiktionaryParser
import urllib.request
from bs4 import BeautifulSoup
import re
from constants import *

parser = WiktionaryParser()

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
    app.run()