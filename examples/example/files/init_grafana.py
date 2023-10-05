import requests
import json
import sys

# source_url = 'http://192.168.178.66:3000/api/datasources'
# dashboard_url = 'http://192.168.178.66:3000/api/dashboards/db'

source_url = 'http://localhost:3000/api/datasources'
dashboard_url = 'http://localhost:3000/api/dashboards/db'

auth = ('admin', 'admin')
headers = {
    'Content-Type': 'application/json'
}

#first datasource
source_pressures= {
    "id": "source_A",
    "name": "Pressures SCBA 42_A",
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
    "id": "source_B",
    "name": "Positions SCBA 42_B",
    "type": "influxdb",
    "url": "http://localhost:8086",
    "access": "proxy",
    "database": "scba_42_positions",
    "jsonData": {
      "httpMode": "GET"
    },    
    "overwrite": True
}

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

def put_request(url, auth, headers, source_content)-> str:
    try:
        # Die PUT-Anfrage durchführen
        response = requests.put(
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


response_source_pressures = post_request(source_url, auth, headers, source_pressures)
if response_source_pressures is None:
  response_source_pressures = put_request(source_url, auth, headers, source_pressures)
  if response_source_pressures is None:
    print("Cannot create Data Source for Pressure. Exiting")
    sys.exit(0)
  
source_pressures_id = response_source_pressures["datasource"]["id"]
response_source_positions = post_request(source_url, auth, headers, source_positions)
if response_source_positions is None:
    print("Cannot create Data Source for positions. Exiting")
    sys.exit(0)
source_positions_id = response_source_positions["datasource"]["id"]

source_pressures_id = "1"
response_source_positions = "2"

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
          "datasource": f"{response_source_positions}",
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
          "datasource": f"{response_source_positions}",
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
          "datasource": f"{response_source_positions}",
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
response_dashboard_pressure = post_request(dashboard_url, auth, headers, dashboard_pressure)
print(f"{response_dashboard_pressure}")