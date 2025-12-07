import requests
from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)

# TU API REAL EN RAILWAY
URL_RAILWAY = "https://vuelos-flask-production.up.railway.app/"

def limpiar_dato(diccionario, claves_posibles):
    """ Busca un dato probando varias claves mal codificadas """
    for clave in claves_posibles:
        if clave in diccionario and diccionario[clave]:
            return diccionario[clave]
    return "---"

def limpiar_hora(raw):
    """ Deja solo la hora HH:MM si viene con fecha """
    if not raw: return ""
    return raw.split(" ")[1] if " " in raw else raw

def procesar_vuelo(v, tipo):
    # 1. Armar número de vuelo
    cia = limpiar_dato(v, ["Cia.", "CÃ­a.", "C\u00eda.", "CÃ\xada."])
    num = v.get("Vuelo", "")
    vuelo_full = f"{cia} {num}"

    # 2. Matricula y Posición
    matricula = limpiar_dato(v, ["Matricula", "MatrÃ­cula", "Matr\u00c3\u00adcula", "Matrícula"])
    posicion = limpiar_dato(v, ["Posicion", "PosiciÃ³n", "Posici\u00c3\u00b3n", "Posición"])

    # 3. HORARIOS Y LUGARES
    if tipo == "partida":
        lugar = limpiar_dato(v, ["Destino", "Dest"])
        dato_extra = v.get("Puerta", "---")
        
        # Horarios Partida
        prog = limpiar_hora(v.get("STD", ""))
        est  = limpiar_hora(v.get("ETD", ""))
        real = limpiar_hora(v.get("ATD", ""))
        
    else:
        lugar = v.get("Origen", "---")
        dato_extra = v.get("Cinta", "---")
        
        # Horarios Arribo
        prog = limpiar_hora(v.get("STA", ""))
        est  = limpiar_hora(v.get("ETA", ""))
        real = limpiar_hora(v.get("ATA", ""))

    estado = v.get("Remark", "")

    return {
        "vuelo": vuelo_full,
        "lugar": lugar,
        "hora_prog": prog,  # Programada
        "hora_est": est,    # Estimada
        "hora_real": real,  # Real (Aterrizaje/Despegue)
        "matricula": matricula,
        "posicion": posicion,
        "dato_extra": dato_extra,
        "estado": estado
    }

@app.route('/')
def home():
    try:
        return send_file('index.html')
    except Exception as e:
        return f"ERROR: No encuentro el archivo index.html. {e}"

@app.route('/datos-limpios')
def proxy_datos():
    try:
        r = requests.get(URL_RAILWAY, timeout=10)
        if r.status_code != 200: return jsonify({"error": "Error Railway"}), 500

        datos_crudos = r.json()
        datos_limpios = {"partidas": [], "arribos": []}

        if "partidas" in datos_crudos:
            for p in datos_crudos["partidas"]:
                datos_limpios["partidas"].append(procesar_vuelo(p, "partida"))

        if "arribos" in datos_crudos:
            for a in datos_crudos["arribos"]:
                datos_limpios["arribos"].append(procesar_vuelo(a, "arribo"))

        return jsonify(datos_limpios)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--- SERVIDOR LOCAL v10 INICIADO ---")
    app.run(port=5000, debug=True)

if __name__ == '__main__':
    # Obtiene el puerto del entorno de la nube, si no existe usa el 5000
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' es OBLIGATORIO para que sea visible en internet
    app.run(host='0.0.0.0', port=port)