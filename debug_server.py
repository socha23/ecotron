from powered_up.debug import start_debug_server

import logging

logging.basicConfig(level=logging.INFO)

MOVE_HUB_MAC = "00:16:53:a8:ec:58"
TECHNIC_HUB_MAC = "90:84:2b:5c:2b:9e"

start_debug_server(TECHNIC_HUB_MAC)
