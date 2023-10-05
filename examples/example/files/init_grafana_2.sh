curl -X POST \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "42",
    "name": "Pressures SCBA 42_a",
    "type": "influxdb",
    "url": "http://localhost:8086",
    "access": "proxy",
    "database": "scba_42_pressures",
    "jsonData": {
      "httpMode": "GET"
    }
  }' \
  http://localhost:3000/api/datasources

curl -X POST \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "43",
    "name": "Positions SCBA 42",
    "type": "influxdb",
    "url": "http://localhost:8086",
    "access": "proxy",
    "database": "scba_42_positions",
    "jsonData": {
      "httpMode": "GET"
    }
  }' \
  http://localhost:3000/api/datasources

curl -X POST \
  -u "admin:admin" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboard": {
      "id": null,
      "title": "Pressures_3",
      "panels": [
        {
          "id": 1,
          "type": "graph",
          "title": "Pressures",
          "datasource": "42",
          "targets": [
            {
              "query": "SELECT time,pressure FROM dtmi_influx_Pressure_In WHERE time >= now() - 30m",
              "rawQuery": true
            }
          ],
          "legend": {
            "show": true
          }
        }
      ],
      "timezone": "browser",
      "editable": true
    },
    "overwrite": false
  }' \
  http://localhost:3000/api/dashboards/db
