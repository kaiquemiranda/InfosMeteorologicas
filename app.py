from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import datetime as dt
import meteomatics.api as api
import requests

app = Flask(__name__)
CORS(app)

# Configurações da API Meteomatics
username = 'box7_rebelo_kaique'
password = 'zlWB7I9lW7'
parameters = ['t_2m:C', 'precip_1h:mm', 'wind_speed_10m:ms']
model = 'mix'
startdate = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
enddate = startdate + dt.timedelta(days=1)
interval = dt.timedelta(hours=1)

# Função para obter os dados meteorológicos para uma determinada região
def get_weather_data(coordinates):
    df = api.query_time_series(coordinates, startdate, enddate, interval, parameters, username, password, model=model)
    temperature = df['t_2m:C'].values[0]
    precipitation = df['precip_1h:mm'].values[0]
    wind_speed = df['wind_speed_10m:ms'].values[0]
    return {'temperature': temperature, 'precipitation': precipitation, 'wind_speed': wind_speed}

# Função para obter o nome do bairro com base nas coordenadas
def get_neighborhood_name(lat, lng):
    response = requests.get(f'https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}')
    data = response.json()
    address = data.get('address', {})
    neighborhood = address.get('neighbourhood') or address.get('suburb') or address.get('city_district') or 'Desconhecido'
    return neighborhood

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    # Recebe as coordenadas do clique no mapa
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')

    # Obtemos o nome do bairro
    neighborhood = get_neighborhood_name(lat, lng)

    # Obtemos os dados meteorológicos
    coordinates = [(lat, lng)]
    weather_data = get_weather_data(coordinates)

    # Adicionamos o nome do bairro aos dados meteorológicos
    weather_data['neighborhood'] = neighborhood

    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True)
