curl -X POST-u "admin:admin" -H "Content-Type: application/json"-d '{"name": "Test_Source_script","type": "influxdb","url": "http://localhost:8086","access": "proxy","database": "scba_42_pressures","jsonData": {"httpMode": "GET"}}' localhost:3000/api/datasources

