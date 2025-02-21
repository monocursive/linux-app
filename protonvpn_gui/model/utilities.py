import requests
from ..logger import logger
import time
import psutil
from protonvpn_nm_lib.constants import VIRTUAL_DEVICE_NAME
import json


one_byte_in_kBs = 0.000976
one_byte_in_mBs = 9.76e-7
one_kilobyte_in_bytes = 1000
one_megabyte_in_bytes = 1024590.163934


class Utilities:

    @staticmethod
    def get_ip():
        logger.debug("Getting IP")
        try:
            r = requests.get(
                "https://api.protonvpn.ch/vpn/location", timeout=3
            )
            api_response = r.text
            api_response = json.loads(api_response)
        except (Exception, requests.exceptions.BaseHTTPError) as e:
            logger.exception(e)
            api_response = {
                "IP": None,
                "Lat": None,
                "Long": None,
                "Country": None,
                "ISP": None
            }

        logger.debug("IP fetched")
        vpn_loc = VPNLocation.new(api_response)

        return vpn_loc

    @staticmethod
    def get_network_speed():
        """Get current network speed.

        It searches for a interface that is defined within the library.

        Returns:
            list
        """
        t0 = time.time()
        interface = VIRTUAL_DEVICE_NAME
        dt = 3
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            return []
        tot = (counter.bytes_sent, counter.bytes_recv)

        last_tot = tot
        time.sleep(dt)
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            return []

        t1 = time.time()
        tot = (counter.bytes_sent, counter.bytes_recv)
        ul, dl = [
            (now - last) / (t1 - t0)
            for now, last
            in zip(tot, last_tot)
        ]
        ul = Utilities.convert_network_speed(ul)
        dl = Utilities.convert_network_speed(dl)
        return [ul, dl]

    @staticmethod
    def convert_network_speed(byte_per_second):
        """Convert network speed.

        Converts and return
        the speed  easy readeable units:
            - Bytes per second
            - Kilobytes per second
            - Megabytes per second

        Args:
            byte_per_second(int|float)

        Returns:
            string
        """
        if byte_per_second <= 0:
            return "0 B/s"

        if (
            byte_per_second >= one_kilobyte_in_bytes
            and byte_per_second < one_megabyte_in_bytes
        ):
            return str(
                round((byte_per_second * one_byte_in_kBs), 1)
            ) + " KB/s"
        elif byte_per_second >= one_megabyte_in_bytes:
            return str(
                round((byte_per_second * one_byte_in_mBs), 1)
            ) + " MB/s"
        else:
            return str(int(byte_per_second)) + " B/s"


class VPNLocation:
    IP = None
    LATITUDE = None
    LONGITUDE = None
    COUNTRY_CODE = None
    ISP = None

    def new(api_response):
        vpn_loc = VPNLocation()
        vpn_loc.IP = api_response.get("IP")
        vpn_loc.LATITUDE = api_response.get("Lat")
        vpn_loc.LONGITUDE = api_response.get("Long")
        vpn_loc.COUNTRY_CODE = api_response.get("Country")
        vpn_loc.ISP = api_response.get("ISP")

        return vpn_loc
