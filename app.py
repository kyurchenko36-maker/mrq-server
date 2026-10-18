from flask import Flask, request, jsonify
import json
import os
import random
import string
# Мы убрали import requests, так как сервер больше не отправляет сообщения в Telegram

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

# Создание нового ключа (вызывается из Mavibot)
@app.route('/add_key', methods=['POST'])
def add_key():
    # Получаем количество дней из запроса бота
    data = request.json
    days = data.get('days', 7) # По умолчанию 7 дней

    part1 = ''.join(random.choices(string.ascii_uppercase, k=4))
    part2 = ''.join(random.choices(string.digits, k=4))
    new_key = f"MRQ-{part1}-{part2}"
    
    keys = load_keys()
    # Сохраняем не только HWID, но и срок действия (days)
    keys[new_key] = {"status": "active", "hwid": None, "days": days}
    save_keys(keys)
    
    return jsonify({"status": "success", "key": new_key})

# Проверка ключа (вызывается из лоадера)
@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.json
    user_key = data.get('key')
    user_hwid = data.get('hwid') # Получаем уникальный ID ПК от лоадера
    
    keys = load_keys()
    
    if user_key in keys:
        key_data = keys[user_key]
        
        # Если ключ уже привязан к какому-то ПК
        if key_data.get("hwid") is not None:
            if key_data["hwid"] == user_hwid:
                return jsonify({"status": "success", "message": "Ключ верный"})
            else:
                return jsonify({"status": "error", "message": "Ключ уже активирован на другом ПК"})
        else:
            # Если ключ новый, привязываем его к этому ПК (первый запуск)
            key_data["hwid"] = user_hwid
            save_keys(keys)
            return jsonify({"status": "success", "message": "Ключ успешно активирован"})
            
    return jsonify({"status": "error", "message": "Неверный ключ"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
