from flask import Flask, request, jsonify
import json
import os
import random
import string
import datetime

app = Flask(__name__)
KEYS_FILE = "keys.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f)

@app.route('/add_key', methods=['POST'])
def add_key():
    data = request.json
    days = data.get('days', 7)
    
    part1 = ''.join(random.choices(string.ascii_uppercase, k=4))
    part2 = ''.join(random.choices(string.digits, k=4))
    new_key = f"MRQ-{part1}-{part2}"
    
    keys = load_keys()
    # Запоминаем дату создания ключа
    keys[new_key] = {
        "status": "active", 
        "hwid": None, 
        "days": days,
        "created_at": str(datetime.date.today())
    }
    save_keys(keys)
    
    return jsonify({"status": "success", "key": new_key})

@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.json
    user_key = data.get('key')
    user_hwid = data.get('hwid')
    
    keys = load_keys()
    
    if user_key in keys:
        key_data = keys[user_key]
        
        # Проверяем, не истек ли срок
        created_at = datetime.datetime.strptime(key_data["created_at"], "%Y-%m-%d").date()
        days_passed = (datetime.date.today() - created_at).days
        days_left = key_data["days"] - days_passed
        
        if days_left <= 0:
            return jsonify({"status": "error", "message": "Срок действия ключа истек"})
            
        # Проверяем HWID
        if key_data.get("hwid") is not None:
            if key_data["hwid"] == user_hwid:
                return jsonify({"status": "success", "message": "Ключ верный", "days_left": days_left})
            else:
                return jsonify({"status": "error", "message": "Ключ уже активирован на другом ПК"})
        else:
            key_data["hwid"] = user_hwid
            save_keys(keys)
            return jsonify({"status": "success", "message": "Ключ успешно активирован", "days_left": days_left})
            
    return jsonify({"status": "error", "message": "Неверный ключ"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
