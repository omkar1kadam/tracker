from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Store the latest GPS coordinates and route history
latest_coords = {"latitude": 0.0, "longitude": 0.0}
route_history = []  # list of [lat, lng] points

@app.route('/gps', methods=['POST'])
def gps_data():
    global latest_coords, route_history
    data = request.get_json()
    print(f"📍 Received GPS Data: {data}")

    lat = float(data['latitude'])
    lng = float(data['longitude'])

    # Update latest coordinates
    latest_coords["latitude"] = lat
    latest_coords["longitude"] = lng

    # Add to route history
    route_history.append([lat, lng])

    # Save to file
    with open("gps_log.txt", "a") as f:
        f.write(f"{lat}, {lng}\n")

    return jsonify({"status": "success", "message": "GPS data received"}), 200

@app.route('/coords')
def get_coords():
    """Send latest coordinates and full route history to the frontend."""
    return jsonify({
        "latest": latest_coords,
        "route": route_history
    })

@app.route('/map')
def map_page():
    """Serve a live map page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live GPS Tracker with Route</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <style>
            #map { height: 100vh; width: 100%; }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([0, 0], 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19
            }).addTo(map);

            var marker = L.marker([0, 0]).addTo(map);
            var routeLine = L.polyline([], {color: 'red'}).addTo(map);

            async function updateLocation() {
                let res = await fetch('/coords');
                let data = await res.json();

                let lat = data.latest.latitude;
                let lng = data.latest.longitude;
                let route = data.route;

                // Update marker position
                marker.setLatLng([lat, lng]);
                map.setView([lat, lng], 15);

                // Update route polyline
                routeLine.setLatLngs(route);
            }

            // Update every 2 seconds
            setInterval(updateLocation, 2000);

            updateLocation();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
