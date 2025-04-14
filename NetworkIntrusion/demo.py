import numpy as np
import pandas as pd
from scapy.all import sniff, IP, TCP, UDP
import time
import pickle
import socket
import struct
import platform
from fastapi import FastAPI
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Function to convert IP to integer
def ip2int(ip):
    try:
        return struct.unpack("!L", socket.inet_aton(ip))[0]
    except socket.error:
        return 0  # Default for malformed IPs

# Load trained model & scaler
with open("networkIntrusion.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# List to store captured packet data
packet_data = []

# Callback function to process packets
def packet_callback(packet):
    global packet_data  

    if IP in packet:  # Only process IP packets
        try:
            timestamp = time.time()  # Current timestamp
            src_ip = ip2int(packet[IP].src)
            dst_ip = ip2int(packet[IP].dst)
            proto = packet[IP].proto
            length = len(packet)

            # Extract ports for TCP/UDP packets
            src_port, dst_port = 0, 0  # Default for non-TCP/UDP packets
            if TCP in packet:
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif UDP in packet:
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport

            # Print packet details
            print(f"[{timestamp}] {packet[IP].src}:{src_port} -> {packet[IP].dst}:{dst_port} (Proto: {proto}, Length: {length})")

            # Append to list
            packet_data.append([timestamp, src_ip, dst_ip, proto, src_port, dst_port, length])
        except Exception as e:
            print(f"⚠ Error processing packet: {e}")

# Automatically detect network interface
def get_network_interface():
    system = platform.system()
    if system == "Windows":
        return "Wi-Fi"  # Change if using Ethernet (e.g., "Ethernet")
    elif system == "Linux":
        return "eth0"  # Common default on Linux
    elif system == "Darwin":  # macOS
        return "en0"
    return None

# Capture live network packets
network_interface = get_network_interface()

if not network_interface:
    print("❌ No valid network interface detected. Exiting.")
else:
    print(f"📡 Capturing packets on {network_interface}... Press Ctrl+C to stop.")
    sniff(iface=network_interface, prn=packet_callback, count=15)  

    # Ensure predictions only run if packets exist
    if len(packet_data) == 0:
        print("❌ No packets captured. Exiting.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(packet_data, columns=["Timestamp", "Source IP", "Destination IP", "Protocol", "Source Port", "Destination Port", "Length"])

        # Apply feature scaling
        df_scaled = scaler.transform(df)

        # Predict using the trained model
        predictions = model.predict(df_scaled)

        # Convert numerical labels back to original categories
        predicted_labels = label_encoder.inverse_transform(predictions)

        # Display results
        print("\n🔍 Prediction Results:")
        for i, label in enumerate(predicted_labels):
            print(f"Packet {i+1}: {label}")

        if "Malware" in predicted_labels:
            print("🚨 Malware Detected!")

# FastAPI Endpoint for External Packet Analysis
@app.post("/predict")
def predict():
    try:
        global packet_data

        # Ensure we have packets to analyze
        if len(packet_data) == 0:
            return {"error": "No packets captured."}

        # Convert to DataFrame
        df = pd.DataFrame(packet_data, columns=["Timestamp", "Source IP", "Destination IP", "Protocol", "Source Port", "Destination Port", "Length"])

        # Apply feature scaling
        df_scaled = scaler.transform(df)

        # Predict using the trained model
        predictions = model.predict(df_scaled)

        # Convert numerical labels back to original categories
        predicted_labels = label_encoder.inverse_transform(predictions)

        return {"predictions": predicted_labels.tolist()}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)