import machine
import network
import socket
import time

# Set up MQ-2 gas sensor
mq2_pin = machine.Pin(12, machine.Pin.IN)

# Set up WiFi network
SSID = "Trojan"
PASSWORD = "my_Trojan"
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

# HTML page with JavaScript to update the gas level
html = """<!DOCTYPE html>
<html>
<head>
    <script>
        function updateGasLevel() {{
            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {{
                if (this.readyState == 4 && this.status == 200) {{
                    document.getElementById("gas-level").innerHTML = this.responseText;
                }}
            }};
            xhttp.open("GET", "/gas-level", true);
            xhttp.send();
        }}
        setInterval(updateGasLevel, 1000);
    </script>
</head>
<body>

<h1>Gas Level: <span id="gas-level">{0}</span></h1>

</body>
</html>
"""

# Function to read the gas level from the MQ-2 sensor
def read_gas_level():
    value = 0
    for i in range(200):
        value += mq2_pin.value()
    value /= 200
    return value

# Function to handle incoming web requests
def handle_request(conn):
    request = conn.recv(1024)
    request = str(request)
    if "/gas-level" in request:
        gas_level = read_gas_level()
        response = "Gas level: " + str(gas_level)
    else:
        response = html.format("")
    conn.send(response)
    conn.close()

# Wait for incoming web requests
while True:
    conn, addr = s.accept()
    handle_request(conn)
