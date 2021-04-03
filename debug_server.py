from powered_up.debug import start_debug_server

import logging

TECHNIC_HUB_MAC = "90:84:2b:5c:2b:9e"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_debug_server(TECHNIC_HUB_MAC)
