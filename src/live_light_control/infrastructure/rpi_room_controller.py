import requests

from live_light_control.domain.devices.controller import RoomController

url = "http://raspberrypi.local:8000"


class RPiRoomController(RoomController):
    def set_global_color(self, color, ms=0):
        requests.put(f"{url}/global/color/{color}?ms={ms}")

    def set_global_intensity(self, value, ms=0):
        requests.put(f"{url}/global/intensity/{value}?ms={ms}")