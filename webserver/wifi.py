import network
import json


class ConfigFileNotFoundError(Exception):
    pass


def read_connection_details_from_file(config_filepath='config.json') -> tuple[str, str]:
    try:
        with open(config_filepath, 'r') as config_file:
            data = config_file.read()
            connection_details = json.loads(data)
            return connection_details['ssid'], connection_details['psk']
    except OSError:
        raise ConfigFileNotFoundError()


def connect(ssid: str, psk: str) -> network.WLAN:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, psk)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan
