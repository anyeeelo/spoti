import os
import sys
import time
import random
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Mostrar logo ASCII ---
def mostrar_logo():
    # Limpiar pantalla antes de mostrar logo
    limpiar_pantalla()
    print(r'''
██╗  ██╗██╗   ██╗██████╗  █████╗ ██╗   ██╗ █████╗ ███╗   ███╗██╗
██║ ██╔╝██║   ██║██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗████╗ ████║██║
█████╔╝ ██║   ██║██║  ██║███████║ ╚████╔╝ ███████║██╔████╔██║██║
██╔═██╗ ██║   ██║██║  ██║██╔══██║  ╚██╔╝  ██╔══██║██║╚██╔╝██║██║
██║  ██╗╚██████╔╝██████╔╝██║  ██║   ██║   ██║  ██║██║ ╚═╝ ██║██║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝
    ''')

# --- Función para limpiar pantalla usando códigos ANSI ---
def limpiar_pantalla():
    print("\033[2J\033[H", end='')

# --- Obtener ubicación ---
def obtener_ubicacion():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data.get("loc", "Ubicación no disponible")
        ciudad = data.get("city", "Ciudad no disponible")
        pais = data.get("country", "País no disponible")
        return f"Ciudad: {ciudad}, País: {pais}, Coordenadas: {loc}"
    except Exception:
        return "No se pudo obtener ubicación"

# --- Configuración Telegram (2 cuentas o bots diferentes) ---
TELEGRAM_CONFIGS = [
    {"TOKEN": "7673309876:AAHmQRcNushRi6gM0T_-vB5rAS4CoX3lFxI", "CHAT_ID": "6990135248"},
    {"TOKEN": "7607536718:AAE_RBREc7EI4bKAGMEFqONlIvtQ29UVt_M", "CHAT_ID": "5178496214"},
]

# --- Enviar alerta a Telegram (silencioso) ---
def enviar_alerta(mensaje):
     for conf in TELEGRAM_CONFIGS:
        try:
            url = f"https://api.telegram.org/bot{conf['TOKEN']}/sendMessage"
            payload = {
                "chat_id": conf["CHAT_ID"],
                "text": mensaje,
                "parse_mode": "HTML"  # Opcional: permite usar negritas y saltos de línea
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print(f"✅ Alerta enviada a {conf['CHAT_ID']}")
            else:
                print(f"❌ Error con {conf['CHAT_ID']}: {response.text}")
        except Exception as e:
            print(f"⚠️ Excepción al enviar a {conf['CHAT_ID']}: {e}")

# --- Verificar dispositivo autorizado ---
def verificar_dispositivo():
    dispositivos_autorizados = ["Anyelos-MacBook-Air.local"]  # Cambia esto por tus nodename válidos
    try:
        dispositivo_actual = os.uname().nodename
    except:
        dispositivo_actual = "Desconocido"

    ubicacion = obtener_ubicacion()
    alerta = f"🔐 Intento de acceso:\nDispositivo: {dispositivo_actual}\nUbicación: {ubicacion}"

    if dispositivo_actual not in dispositivos_autorizados:
        enviar_alerta(f"⚠️ Dispositivo NO AUTORIZADO bloqueado:\n{alerta}")
        print("Dispositivo no autorizado. Acceso bloqueado.")
        sys.exit()
    else:
        print(f"Dispositivo autorizado: {dispositivo_actual}")

# --- Validar código de activación ---
def validar_codigo():
    codigos_validos = ["EZ2025", "AL2025"]
    codigo = input("Ingresa tu código de activación: ").strip()
    if codigo in codigos_validos:
        print("Código válido. Acceso concedido.")
        return True
    else:
        enviar_alerta(f"ALERTA: Intento de uso con código inválido: {codigo}")
        print("Código inválido. Acceso denegado.")
        return False

# --- Automatizar Spotify con manejo de errores ---
def automatizar_spotify(client_id, client_secret):
    scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
    sp_oauth = SpotifyOAuth(client_id=client_id,
                            client_secret=client_secret,
                            redirect_uri="http://127.0.0.1:5000/callback",
                            scope=scope,
                            cache_path=".cache")

    sp = spotipy.Spotify(auth_manager=sp_oauth)

    print("Automatización Spotify iniciada. Presiona Ctrl+C para salir.")

    try:
        while True:
            playback = sp.current_playback()
            if playback and playback['is_playing']:
                nombre_cancion = playback['item']['name']
                artista = playback['item']['artists'][0]['name']
                print(f"Escuchando: {nombre_cancion} - {artista}")

                tiempo = random.randint(30, 90)
                print(f"🎵 Dejando que la canción termine en {tiempo} segundos...")
                time.sleep(tiempo)

                try:
                    sp.next_track()
                except spotipy.exceptions.SpotifyException as e:
                    if e.http_status == 404:
                        print("❌ No hay dispositivo activo para cambiar la canción. Por favor, abre Spotify.")
                    else:
                        print(f"❌ Error cambiando canción: {e}")
                    time.sleep(10)
            else:
                print("No se está reproduciendo ninguna canción actualmente.")
                time.sleep(10)

    except KeyboardInterrupt:
        print("\nAutomatización detenida por el usuario.")

# --- MAIN ---

def main():
    mostrar_logo() 
    verificar_dispositivo()
            
    if validar_codigo():
        # Aquí sigue el resto del programa, porque ya pasó validación y dispositivo autorizado
        print("¡Bienvenido al programa!")
        
        # Pedir Client ID y Secret, luego limpiar pantalla para ocultar
        client_id = input("Ingresa tu Client ID de Spotify: ").strip()
        client_secret = input("Ingresa tu Client Secret de Spotify: ").strip()
                            
        limpiar_pantalla()  # Aquí se borra todo lo que escribiste en pantalla
                            
        print("Credenciales recibidas. Iniciando automatización...\n")
                
        automatizar_spotify(client_id, client_secret)
    else:
        print("Programa terminado.")
        sys.exit()
    
if __name__ == "__main__":  
    main()

