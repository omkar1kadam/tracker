from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Store latest GPS coordinates and route history
latest_coords = {"latitude": 0.0, "longitude": 0.0}
route_history = []


@app.route('/gps', methods=['POST'])
def gps_data():
    global latest_coords, route_history
    data = request.get_json()
    print(f"📍 Received GPS Data: {data}")

    lat = float(data['latitude'])
    lng = float(data['longitude'])

    latest_coords["latitude"] = lat
    latest_coords["longitude"] = lng
    route_history.append([lat, lng])

    with open("gps_log.txt", "a") as f:
        f.write(f"{lat}, {lng}\n")

    return jsonify({"status": "success", "message": "GPS data received"}), 200


@app.route('/coords')
def get_coords():
    return jsonify({
        "latest": latest_coords,
        "route": route_history
    })


@app.route('/map')
def map_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live GPS Tracker (Google Maps)</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            #map {
                height: 100vh;
                width: 100%;
            }
        </style>
        <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
    </head>
    <body>
        <div id="map"></div>

        <script>
            let map;
            let marker;
            let routePath;
            let firstUpdate = true;

            function initMap() {
                map = new google.maps.Map(document.getElementById('map'), {
                    center: {lat: 0, lng: 0},
                    zoom: 15
                });

                marker = new google.maps.Marker({
                    position: {lat: 0, lng: 0},
                    map: map,
                    title: "Current Location"
                });

                routePath = new google.maps.Polyline({
                    path: [],
                    geodesic: true,
                    strokeColor: '#FF0000',
                    strokeOpacity: 1.0,
                    strokeWeight: 2
                });
                routePath.setMap(map);

                updateLocation();
                setInterval(updateLocation, 2000);
            }

            async function updateLocation() {
                let res = await fetch('/coords');
                let data = await res.json();

                let lat = data.latest.latitude;
                let lng = data.latest.longitude;
                let route = data.route.map(coord => ({lat: coord[0], lng: coord[1]}));

                marker.setPosition({lat: lat, lng: lng});

                if (firstUpdate) {
                    map.setCenter({lat: lat, lng: lng});
                    firstUpdate = false;
                }

                routePath.setPath(route);
            }

            window.onload = initMap;
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
