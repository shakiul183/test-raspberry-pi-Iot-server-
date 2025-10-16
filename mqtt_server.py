import paho.mqtt.client as mqtt
import json
import random
import time
from datetime import datetime

BROKER = "13.201.125.205"
PORT = 1883
CLIENT_ID = "Server001"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Server] Connected to MQTT Broker!")
        client.subscribe("myiot/device/data")
        print("[Server] Subscribed to myiot/device/data")
    else:
        print(f"[Server] Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"[Server] Received from Pi on topic '{msg.topic}': {msg.payload.decode()}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"[Server] Subscribed successfully with QoS: {granted_qos}")

client = mqtt.Client(client_id=CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

try:
    client.connect(BROKER, PORT, keepalive=60)
    print(f"[Server] Connecting to {BROKER}:{PORT}...")
except Exception as e:
    print(f"[Server] Connection failed: {e}")
    exit(1)

client.loop_start()

try:
    while True:
        payload = {
            "device_id": CLIENT_ID,
            "timestamp": datetime.utcnow().isoformat(),
            "sensors": {f"sensor{i}": random.uniform(i*10, (i+1)*10) for i in range(1,11)},
            "status": "from AWS server"
        }
        result = client.publish("myiot/server/data", json.dumps(payload), qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[Server] Sent to myiot/server/data: {payload['status']}")
        else:
            print(f"[Server] Failed to send message, rc: {result.rc}")
        time.sleep(7)
except KeyboardInterrupt:
    print("\n[Server] Shutting down...")
    client.loop_stop()
    client.disconnect()