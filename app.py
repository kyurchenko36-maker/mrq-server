from flask import Flask, request, jsonify
import json
import os
import random
import string
import requests

app = Flask(__name__)
KEYS_FILE = "keys.json"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f)

@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.json
    user_key = data.get('key')
    keys = load_keys()
    if user_key in keys:
        return jsonify({"status": "success", "message": "Ключ верный"})
    return jsonify({"status": "error", "message": "Неверный ключ"})

@app.route('/add_key', methods=['POST'])
def add_key():
    data = request.json
    chat_id = data.get('chat_id')

    part1 = ''.join(random.choices(string.ascii_uppercase, k=4))
    part2 = ''.join(random.choices(string.digits, k=4))
    new_key = f"MRQ-{part1}-{part2}"
    
    keys = load_keys()
    keys[new_key] = {"status": "active"}
    save_keys(keys)
    
    return jsonify({"status": "success", "key": new_key})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
