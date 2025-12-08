import requests
from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)

# TU API REAL EN RAILWAY
URL_RAILWAY = "https://vuelos-flask-production.up.railway.app/datos-limpios"

@app.route('/')
def home():
    try:
        return send_file('index.html')
    except Exception as e:
        return f"ERROR: No encuentro index.html. {e}"

# Servir imagen del plano
@app.route('/plano.jpg')
def servir_imagen():
    try:
        return send_file('plano.jpg')
    except Exception as e:
        return f"ERROR: No encuentro la imagen plano.jpg. {e}"

# PROXY SIMPLE - Solo pasa los datos tal cual
@app.route('/datos-limpios')
def proxy_datos():
    try:
        print(f"→ Requesting data from Railway...")
        r = requests.get(URL_RAILWAY, timeout=15)
        
        if r.status_code != 200:
            print(f"✗ Railway error: {r.status_code}")
            return jsonify({"error": f"Railway HTTP {r.status_code}"}), 500
        
        datos = r.json()
        
        # Verificar que tenga datos
        if 'partidas' in datos and 'arribos' in datos:
            total = len(datos.get('partidas', [])) + len(datos.get('arribos', []))
            print(f"✓ Datos recibidos: {total} vuelos")
            
            # Pasar los datos tal cual (ya están en el formato correcto)
            return jsonify(datos), 200
        else:
            print(f"✗ Formato inesperado: {list(datos.keys())}")
            return jsonify({"error": "Formato de datos incorrecto"}), 500
            
    except requests.Timeout:
        print("✗ Timeout conectando a Railway")
        return jsonify({"error": "Timeout - Railway no responde"}), 504
    except requests.RequestException as e:
        print(f"✗ Error de conexión: {e}")
        return jsonify({"error": f"Error conectando a Railway: {str(e)}"}), 500
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 SERVIDOR INICIADO EN PUERTO {port}")
    print(f"📡 Conectando a: {URL_RAILWAY}")
    app.run(host='0.0.0.0', port=port, debug=False)
