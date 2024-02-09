import json
import logging
import sys
import time
from machine import Pin
from wifi import connect, read_connection_details_from_file
from picoweb import WebApp, start_response


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

connected_wifi = connect(*read_connection_details_from_file())
my_address = connected_wifi.ifconfig()[0]

app = WebApp(__name__)

on_pin = Pin(14, Pin.OUT)
off_pin = Pin(15, Pin.OUT)

on_pin.on()
off_pin.off()


# On:
# - on_pin = GND
# - off_pin = false
# Off:
# - on_pin = true
# - off_pin = 3V3


def turn_off():
    on_pin.off()
    off_pin.on()
    time.sleep(1.0)
    on_pin.off()
    off_pin.off()


def turn_on():
    on_pin.on()
    off_pin.off()
    time.sleep(1.0)
    on_pin.off()
    off_pin.off()

@app.route("/time")
def time_get(req, resp):
    req.parse_qs()

    now = time.time()
    json_str = json.dumps({"time": now})

    yield from start_response(resp, status=200, content_type="text/json")
    yield from resp.awrite(json_str.encode())


@app.route("/switch/on")
def switch_on(req, resp):
    turn_on()

    yield from start_response(resp, status=200)


@app.route("/switch/off")
def switch_on(req, resp):
    turn_off()
    yield from start_response(resp, status=200)


turn_on()

app.run(debug=True, host=my_address, port=8080, lazy_init=False, log=logging.getLogger())