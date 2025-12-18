import paho.mqtt.client as mqtt
# TODO maybe switching to more common pygame.midi
import rtmidi.midiutil as midi
import argparse
import time


class Midi2Broker:
    """Receiving MIDI events and sending them to an MQTT broker."""

    def __init__(self, host, port, username, password, midi_port, topicprefix):
        self.topicprefix = topicprefix
        self.midiin, port_name = midi.open_midiinput(midi_port)
        
        print("listening to midi device", port_name)
        self.midiin.set_callback(self.on_midi_event)

        print("connecting and sending messages to", host, port)
        self.mqtt = mqtt.Client()

        if username and password:
            self.mqtt.username_pw_set(username, password)
        
        self.mqtt.connect(host, port)

    def on_midi_event(self, event, data=None):
        message, _ = event
        chan, note, val = message

        self.publish(
            self.topicprefix+"/chan/{0}/note/{1}/".format(chan, note), val)

    def publish(self, topic, payload):
        print("publishing message", topic, payload)
        self.mqtt.publish(topic, payload)

    def start_loop(self):
        """Run an endless loop and wait for events."""
        while True:
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
                        help="Host of the MQTT-Broker, defaults to localhost",
                        default="localhost")
    parser.add_argument('--port',
                        help="Port of the MQTT-Broker, default: 1883",
                        type=int, default=1883)
    parser.add_argument('--username',
                        help="Set username for MQTT-Broker authentication",
                        type=str)
    parser.add_argument('--password',
                        help="Set password for MQTT-Broker authentication",
                        type=str)
    parser.add_argument('--midiport',
                        help="Port of the MIDI Interface, default:1",
                        type=int, default=0)
    parser.add_argument('--topicprefix',
                        help="Prefix for the MQTT topic default:midi",
                        type=str, default="midi")
    args = parser.parse_args()

    client = Midi2Broker(args.host,
                         args.port,
                         args.username,
                         args.password,
                         args.midiport,
                         args.topicprefix)
    
    client.start_loop()

    print("finished")

if __name__ == "__main__":
    main()
