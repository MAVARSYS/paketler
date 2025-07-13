from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

ENGEL_DOSYA = "engeller.json"
HEDEF_DOSYA = "hedef_koordinat.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/engel_ekle', methods=['POST'])
def engel_ekle():
    data = request.get_json()
    if not data or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'Eksik veri'}), 400

    if os.path.exists(ENGEL_DOSYA):
        with open(ENGEL_DOSYA, 'r', encoding='utf-8') as f:
            engeller = json.load(f)
    else:
        engeller = []

    engeller.append({'lat': data['lat'], 'lon': data['lon']})

    with open(ENGEL_DOSYA, 'w', encoding='utf-8') as f:
        json.dump(engeller, f, indent=2, ensure_ascii=False)

    return jsonify({'status': 'Engel başarıyla eklendi'})

@app.route('/api/hedef_kaydet', methods=['POST'])
def hedef_kaydet():
    data = request.get_json()
    if not data or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'Eksik veri'}), 400

    with open(HEDEF_DOSYA, 'w', encoding='utf-8') as f:
        json.dump({'lat': data['lat'], 'lon': data['lon']}, f, indent=2, ensure_ascii=False)

    return jsonify({'status': 'Hedef başarıyla kaydedildi'})

if __name__ == '__main__':
    app.run(debug=True)
