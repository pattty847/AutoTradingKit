# python 3.11
import json
import logging
import random
import time

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTv5
from paho.mqtt.subscribeoptions import SubscribeOptions


class Config:
    """
    Application Configuration Class
    """
    BROKER = 'datafeed-lts.dnse.com.vn'
    PORT = 443
    TOPICS = ("plaintext/quotes/derivative/OHLC/1/VN30F1M", "plaintext/quotes/stock/tick/+")
    CLIENT_ID = f'python-json-mqtt-ws-sub-{random.randint(0, 1000)}'
    USERNAME = 'investor'
    PASSWORD = 'token'
    FIRST_RECONNECT_DELAY = 1
    RECONNECT_RATE = 2
    MAX_RECONNECT_COUNT = 12
    MAX_RECONNECT_DELAY = 60


class MQTTClient:
    """
    Class encapsulating MQTT Client related functionalities
    """

    def __init__(self):
        self.client = mqtt_client.Client(Config.CLIENT_ID,
                                         protocol=MQTTv5,
                                         transport='websockets')

        self.client.username_pw_set(Config.USERNAME, Config.PASSWORD)
        self.client.tls_set_context()
        self.client.ws_set_options(path="/wss")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.FLAG_EXIT = False

    def connect_mqtt(self):
        self.client.connect(Config.BROKER, Config.PORT, keepalive=120)
        return self.client

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            logging.info("Connected to MQTT Broker!")
            topic_tuple = [(topic, SubscribeOptions(qos=2)) for topic in Config.TOPICS]
            self.client.subscribe(topic_tuple)
        else:
            logging.error(f'Failed to connect, return code {rc}')

    def on_disconnect(self, client, userdata, rc, properties=None):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, Config.FIRST_RECONNECT_DELAY
        while reconnect_count < Config.MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= Config.RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, Config.MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
        self.FLAG_EXIT = True

    def on_message(self, client, userdata, msg):
        logging.debug(f'Topic: {msg.topic}, msg: {msg.payload}')
        payload = json.JSONDecoder().decode(msg.payload.decode())
        logging.debug(f'payload: {payload}')
        logging.debug(f'symbol: {payload["symbol"]}')


def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    my_mqtt_client = MQTTClient()
    client = my_mqtt_client.connect_mqtt()
    client.loop_forever()


if __name__ == '__main__':
    run()