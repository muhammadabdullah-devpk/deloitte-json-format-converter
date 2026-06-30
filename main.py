from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import re

def _parse_iso8601_to_epoch_ms(ts):
    """Parse common ISO-8601 variants to epoch milliseconds."""
    ts = ts.strip()
    ts_norm = re.sub(r'Z$', '+00:00', ts)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(ts_norm, fmt)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    raise ValueError(f"Unrecognised timestamp format: {ts!r}")

def _require_keys(obj, keys, context=""):
    for key in keys:
        if key not in obj:
            raise ValueError(f"Missing required field {key!r}{' in ' + context if context else ''}")

def convertFromFormat1(jsonObject):
    _require_keys(jsonObject, ["deviceID", "deviceType", "timestamp", "location", "operationStatus", "temp"])

    location_str = jsonObject["location"]
    if not isinstance(location_str, str):
        raise ValueError(f"'location' must be a string, got {type(location_str).__name__}")

    locationParts = location_str.split("/")
    if len(locationParts) != 5:
        raise ValueError(
            f"'location' must have exactly 5 '/'-separated segments "
            f"(country/city/area/factory/section), got {len(locationParts)}: {location_str!r}"
        )

    return {
        "deviceID": jsonObject["deviceID"],
        "deviceType": jsonObject["deviceType"],
        "timestamp": jsonObject["timestamp"],
        "location": {
            "country": locationParts[0],
            "city": locationParts[1],
            "area": locationParts[2],
            "factory": locationParts[3],
            "section": locationParts[4]
        },
        "data": {
            "status": jsonObject["operationStatus"],
            "temperature": jsonObject["temp"]
        }
    }

def convertFromFormat2(jsonObject):
    _require_keys(jsonObject, ["device", "timestamp", "country", "city", "area", "factory", "section", "data"])
    _require_keys(jsonObject["device"], ["id", "type"], context="device")

    timestamp = _parse_iso8601_to_epoch_ms(jsonObject["timestamp"])

    return {
        "deviceID": jsonObject["device"]["id"],
        "deviceType": jsonObject["device"]["type"],
        "timestamp": timestamp,
        "location": {
            "country": jsonObject["country"],
            "city": jsonObject["city"],
            "area": jsonObject["area"],
            "factory": jsonObject["factory"],
            "section": jsonObject["section"]
        },
        "data": jsonObject["data"]
    }

def run_tests():
    # --- Format 1: happy path ---
    input_format_1 = {
        "deviceID": "device-123",
        "deviceType": "sensor",
        "timestamp": 1624445837783,
        "location": "japan/tokyo/keiyō-industrial-zone/factory-1/section-2",
        "operationStatus": "active",
        "temp": 22
    }
    expected_output_1 = {
        "deviceID": "device-123",
        "deviceType": "sensor",
        "timestamp": 1624445837783,
        "location": {
            "country": "japan",
            "city": "tokyo",
            "area": "keiyō-industrial-zone",
            "factory": "factory-1",
            "section": "section-2"
        },
        "data": {
            "status": "active",
            "temperature": 22
        }
    }
    assert convertFromFormat1(input_format_1) == expected_output_1, "Format 1 conversion failed!"

    # --- Format 1: bad location (too few segments) ---
    try:
        convertFromFormat1({**input_format_1, "location": "japan/tokyo"})
        assert False, "Should have raised ValueError for short location"
    except ValueError:
        pass

    # --- Format 1: missing required field ---
    try:
        bad = {k: v for k, v in input_format_1.items() if k != "temp"}
        convertFromFormat1(bad)
        assert False, "Should have raised ValueError for missing 'temp'"
    except ValueError:
        pass

    # --- Format 2: happy path with milliseconds + Z ---
    input_format_2 = {
        "device": {"id": "device-456", "type": "camera"},
        "timestamp": "2021-06-23T10:57:17.783Z",
        "country": "japan",
        "city": "tokyo",
        "area": "keiyō-industrial-zone",
        "factory": "factory-1",
        "section": "section-2",
        "data": {"status": "idle", "temperature": 25}
    }
    expected_output_2 = {
        "deviceID": "device-456",
        "deviceType": "camera",
        "timestamp": 1624445837783,
        "location": {
            "country": "japan",
            "city": "tokyo",
            "area": "keiyō-industrial-zone",
            "factory": "factory-1",
            "section": "section-2"
        },
        "data": {"status": "idle", "temperature": 25}
    }
    assert convertFromFormat2(input_format_2) == expected_output_2, "Format 2 conversion failed!"

    # --- Format 2: timestamp without fractional seconds ---
    input_no_ms = {**input_format_2, "timestamp": "2021-06-23T10:57:17Z"}
    result_no_ms = convertFromFormat2(input_no_ms)
    assert result_no_ms["timestamp"] == 1624445837000, \
        f"Format 2 no-ms timestamp failed: {result_no_ms['timestamp']}"

    # --- Format 2: timestamp with timezone offset instead of Z ---
    input_offset = {**input_format_2, "timestamp": "2021-06-23T11:57:17.783+01:00"}
    result_offset = convertFromFormat2(input_offset)
    assert result_offset["timestamp"] == 1624445837783, \
        f"Format 2 offset timestamp failed: {result_offset['timestamp']}"

    # --- Format 2: missing required field ---
    try:
        bad2 = {k: v for k, v in input_format_2.items() if k != "country"}
        convertFromFormat2(bad2)
        assert False, "Should have raised ValueError for missing 'country'"
    except ValueError:
        pass

    print("All tests passed")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default request logging

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        try:
            run_tests()
            response = {"status": "success", "message": "All tests passed"}
        except AssertionError as e:
            response = {"status": "failed", "message": str(e)}
        except Exception as e:
            response = {"status": "error", "message": str(e)}
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == "__main__":
    run_tests()
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Server starting on port {port}...")
    server.serve_forever()
