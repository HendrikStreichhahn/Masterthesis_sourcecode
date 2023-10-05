import requests
import json

# Konfigurationsdaten für die Datenquelle
# grafana_url = "http://grafana.example.com"  # Die URL Ihres Grafana-Servers
# api_key = "Ihr_API-Schlüssel"  # Ihr API-Schlüssel für die Authentifizierung
# datasource_name = "Ihr_Datenquellenname"
# datasource_type = "prometheus"  # Der Typ der Datenquelle (z.B., prometheus, influxdb, etc.)
# datasource_url = "http://prometheus.example.com"  # Die URL Ihrer Datenquelle
# datasource_access = "proxy"  # Der Zugriffsmodus (z.B., direct, proxy, etc.)

def post_request(url, auth, headers, source_content)-> str:
    try:
        # Die POST-Anfrage durchführen
        response = requests.post(
            url,
            json=source_content,
            auth=auth,
            headers=headers)

        # Überprüfen, ob die Anfrage erfolgreich war (Statuscode 200)
        if response.status_code == 200:
            # Die JSON-Antwort auswerten
            json_data = response.json()
            return json_data
        else:
            print(f"Got Responsecode: {response.status_code}")
            json_data = response.json()
            return json_data

    except requests.exceptions.RequestException as e:
        print(f"Cannot send request: {e}")

# Überprüfen, ob die Datenquelle bereits existiert
def datasource_exists(
        grafana_url: str,
        datasource_name: str,
        username: str,
        password: str):
    response = requests.get(
        url = f"{grafana_url}/api/datasources/name/{datasource_name}",
        auth= (username, password),
        headers= {'Content-Type': 'application/json'}
    )
    return response.status_code == 200

def get_datasource(
        grafana_url: str,
        datasource_name: str,
        username: str,
        password: str):
    response = requests.get(
        url = f"{grafana_url}/api/datasources/name/{datasource_name}",
        auth= (username, password),
        headers= {'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None

# Funktion zum Erstellen oder Aktualisieren der Datenquelle
def create_or_update_datasource(
        grafana_url: str,
        datasource_name: str,
        username: str,
        password: str,
        datasource_content) -> str:
    existingDatasource = get_datasource(
        grafana_url,
        datasource_name,
        username,
        password
    )
    if existingDatasource is not None:
        # Datenquelle existiert, aktualisiere sie
        response = requests.put(
            f"{grafana_url}/api/datasources/{existingDatasource['id']}",
            auth= (username, password),
            headers= {'Content-Type': 'application/json'},
            json=datasource_content
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Aktualisieren der Datenquelle: {response.text}")
            print(response.text) 
    else:
        # Datenquelle existiert nicht, erstelle sie
        response = requests.post(
            f"{grafana_url}/api/datasources",
            auth= (username, password),
            headers= {'Content-Type': 'application/json'},
            json=datasource_content
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Erstellen der Datenquelle: {response.text}")

#first datasource
source_pressures= {
    "name": "Pressures_SCBA_42",
    "type": "influxdb",
    "url": "http://localhost:8086",
    "access": "proxy",
    "database": "scba_42_pressures",
    "jsonData": {
      "httpMode": "GET"
    },
    "overwrite": True
}
#second datasource
source_positions = {
    "name": "Positions_SCBA_42",
    "type": "influxdb",
    "url": "http://localhost:8086",
    "access": "proxy",
    "database": "scba_42_positions",
    "jsonData": {
      "httpMode": "GET"
    },    
    "overwrite": True
}


response_source_pressures= create_or_update_datasource(
    "http://localhost:3000",
    "Pressures_SCBA_42",
    "admin",
    "admin",
    source_pressures
)
source_pressures_id = response_source_pressures["datasource"]["id"]
response_source_positions= create_or_update_datasource(
    "http://localhost:3000",
    "Positions_SCBA_42",
    "admin",
    "admin",
    source_positions
)
source_positions_id = response_source_positions["datasource"]["id"]

dashboard_pressure = {
    "dashboard": {
      "id": None,
      "title": "SCBA 42",
      "panels": [
        {
          "id": 1,
          "type": "graph",
          "title": "Pressures",
          "datasource": f"{source_pressures_id}",
          "targets": [
            {
              "query": "SELECT time,pressure FROM dtmi_influx_Pressure_In WHERE time >= now() - 30m",
              "rawQuery": "true"
            }
          ],
          "gridPos": {
            "h": 16,
            "w": 6,
            "x": 0,
            "y": 0
          },
          "legend": {
            "show": True
          },
        },
        {
          "id": 2,
          "type": "graph",
          "title": "Position X",
          "datasource": f"{source_positions_id}",
          "targets": [
            {
              "query": "SELECT time,PositionX FROM dtmi_influx_Position_In WHERE time >= now() - 30m",
              "rawQuery": "true"
            }
          ],
          "gridPos": {
            "h": 16,
            "w": 6,
            "x": 6,
            "y": 0
          },
          "legend": {
            "show": True
          },
        },
        {
          "id": 3,
          "type": "graph",
          "title": "Position Y",
          "datasource": f"{source_positions_id}",
          "targets": [
            {
              "query": "SELECT time,PositionY FROM dtmi_influx_Position_In WHERE time >= now() - 30m",
              "rawQuery": "true"
            }
          ],
          "gridPos": {
            "h": 16,
            "w": 6,
            "x": 12,
            "y": 0
          },
          "legend": {
            "show": True
          },
        },
        {
          "id": 4,
          "type": "graph",
          "title": "Position Z",
          "datasource": f"{source_positions_id}",
          "targets": [
            {
              "query": "SELECT time,PositionZ FROM dtmi_influx_Position_In WHERE time >= now() - 30m",
              "rawQuery": "true"
            }
          ],
          "gridPos": {
            "h": 16,
            "w": 6,
            "x": 18,
            "y": 0
          },
          "legend": {
            "show": True
          },
        }
      ],
      "time": {
        "from": "now-5m",
        "to": "now"
      },
      "timezone": "browser",
      "editable": True
    },
    "overwrite": True
  }

print(f"{json.dumps(dashboard_pressure, indent=4)}")
response_dashboard_pressure = post_request(
    "http://localhost:3000/api/dashboards/db",
    ('admin', 'admin'),
    {'Content-Type': 'application/json'},
    dashboard_pressure)
print(f"{response_dashboard_pressure}")