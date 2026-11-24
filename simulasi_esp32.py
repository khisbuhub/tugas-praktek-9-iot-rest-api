import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"

status_lampu = "OFF"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Terhubung ke Broker Mosquitto Lokal!")
        client.subscribe(TOPIC_KONTROL)
    else:
        print(f"Gagal terhubung, kode error: {reason_code}")

def on_message(client, userdata, msg):
    global status_lampu
    try:
        data = json.loads(msg.payload.decode())
        device = data.get("device", "")
        action = data.get("action", "").upper()
        if device == "lamp" and action in ["ON", "OFF"]:
            status_lampu = action
            print(f"<- Perintah diterima [{msg.topic}]: Lampu sekarang {status_lampu}")
    except Exception as e:
        print("Gagal membaca pesan kontrol:", e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ESP32-Simulator")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

print("ESP32 Simulator berjalan... Tekan Ctrl+C untuk berhenti")

try:
    while True:
        data = {
            "suhu": round(random.uniform(25, 32), 1),
            "kelembaban": round(random.uniform(55, 80), 1),
            "timestamp": datetime.now().isoformat()
        }
        client.publish(TOPIC_SENSOR, json.dumps(data))
        print(f"-> Publish: {data} | Lampu: {status_lampu}")
        time.sleep(3)
except KeyboardInterrupt:
    print("\nSimulator dihentikan.")
    client.loop_stop()
    client.disconnect()