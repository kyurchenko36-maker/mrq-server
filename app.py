from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
KEYS_FILE = "keys.json"

def load_keys():
    # Если файла нет, создаем его с тестовыми ключами
    if not os.path.exists(KEYS_FILE):
        default_keys = {
            "KEY-1111": {"status": "active"},
            "KEY-2222": {"status": "active"},
            "KEY-3333": {"status": "active"}
        }
        with open(KEYS_FILE, "w") as f:
            json.dump(default_keys, f)
        return default_keys
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.json
    user_key = data.get('key')
    keys = load_keys()
    
    if user_key in keys:
        return jsonify({"status": "success", "message": "Ключ верный"})
    else:
        return jsonify({"status": "error", "message": "Неверный ключ"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
