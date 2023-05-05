import machine
import time
import network
import socket
from machine import Pin

# Set up ultrasonic sensor
trigger_pin = Pin(13, Pin.OUT)
echo_pin = Pin(12, Pin.IN)

# Set up WiFi network
SSID = "Your Wifi Name"
PASSWORD = "Your Password"
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)

# Wait for connection
while not sta_if.isconnected():
    pass

# Print IP address
print("Connected to Wi-Fi")
print("IP address:", sta_if.ifconfig()[0])

# Set up web server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

# HTML page with JavaScript and AJAX to update the distance
html = """<!DOCTYPE html>
<html>
<head>
    <script>
        function updateDistance() {{
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {{
                if (this.readyState == 4 && this.status == 200) {{
                    document.getElementById("distance").innerHTML = this.responseText;
                }}
            }};
            xhttp.open("GET", "/distance", true);
            xhttp.send();
        }}
        setInterval(updateDistance, 1000);
    </script>
</head>
<body>

<h1>Distance: <span id="distance">{0}</span> cm</h1>

</body>
</html>
"""

# Function to measure distance using the ultrasonic sensor
def measure_distance():
    # Set trigger pin to LOW for 2 microseconds
    trigger_pin.value(0)
    time.sleep_us(2)
    # Set trigger pin to HIGH for 10 microseconds
    trigger_pin.value(1)
    time.sleep_us(10)
    trigger_pin.value(0)
    # Measure the duration of the pulse on the echo pin
    duration = machine.time_pulse_us(echo_pin, 1, 30000)
    # Calculate distance in cm
    distance = duration / 58.0
    return distance

# Main loop
while True:
    # Accept incoming connections
    conn, addr = s.accept()
    # Read request data
    data = conn.recv(1024)
    # Respond to HTTP requests
    if data.startswith(b"GET / HTTP/1.1"):
        # Send HTML page
        distance = measure_distance()
        response = html.format(distance)
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.send(response)
    elif data.startswith(b"GET /distance HTTP/1.1"):
        # Send distance measurement as plain text
        distance = measure_distance()
        response = "{:.2f}".format(distance)
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/plain\n")
        conn.send("Connection: close\n\n")
        conn.send(response)
    else:
        # Send 404 error for other requests
        conn.send("HTTP/1.1 404 Not Found\n")
        conn.send("Content-Type: text/plain\n")
        conn.send("Connection: close\n\n")
    conn.close()
