import json
import os
import tempfile
import unittest

from leakguard.wake_listener import WakeTracker, arp_sender_ip, load_config, source_mac


class WakeTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tracker = WakeTracker(
            sensors={
                "b8:06:0d:92:2f:5a": {"name": "workshop"},
            },
            wake_quiet_seconds=3.0,
            sleep_quiet_seconds=5.0,
        )

    def test_first_packet_creates_wake_event(self):
        events = self.tracker.on_packet("b8:06:0d:92:2f:5a", now=10.0)

        self.assertEqual(events, [("WAKE", "workshop")])

    def test_packets_within_wake_cycle_do_not_repeat_wake(self):
        self.tracker.on_packet("b8:06:0d:92:2f:5a", now=10.0)

        events = self.tracker.on_packet("b8:06:0d:92:2f:5a", now=11.0)

        self.assertEqual(events, [])

    def test_packet_after_wake_quiet_period_starts_new_wake_cycle(self):
        self.tracker.on_packet("b8:06:0d:92:2f:5a", now=10.0)

        events = self.tracker.on_packet("b8:06:0d:92:2f:5a", now=13.0)

        self.assertEqual(events, [("SLEEP", "workshop"), ("WAKE", "workshop")])

    def test_quiet_sensor_creates_sleep_event(self):
        self.tracker.on_packet("b8:06:0d:92:2f:5a", now=10.0)

        events = self.tracker.collect_sleep_events(now=15.0)

        self.assertEqual(events, [("SLEEP", "workshop")])

    def test_packet_after_sleep_creates_new_wake_event(self):
        self.tracker.on_packet("b8:06:0d:92:2f:5a", now=10.0)
        self.tracker.collect_sleep_events(now=15.0)

        events = self.tracker.on_packet("b8:06:0d:92:2f:5a", now=16.0)

        self.assertEqual(events, [("WAKE", "workshop")])

    def test_unconfigured_mac_is_ignored(self):
        events = self.tracker.on_packet("00:11:22:33:44:55", now=10.0)

        self.assertEqual(events, [])

    def test_source_mac_reads_ethernet_source_address(self):
        frame = b"\xff\xff\xff\xff\xff\xff\xb8\x06\x0d\x92\x2f\x5a" + b"\x08\x06"

        self.assertEqual(source_mac(frame), "b8:06:0d:92:2f:5a")

    def test_arp_sender_ip_reads_ipv4_address(self):
        frame = (
            b"\xff\xff\xff\xff\xff\xff\xb8\x06\x0d\x92\x2f\x5a\x08\x06"
            + b"\x00\x01\x08\x00\x06\x04\x00\x01"
            + b"\xb8\x06\x0d\x92\x2f\x5a\xc0\xa8\x01\x78"
            + b"\x00" * 10
        )

        self.assertEqual(arp_sender_ip(frame), "192.168.1.120")

    def test_load_config_indexes_sensors_by_normalized_mac(self):
        config_data = {
            "interface": "eth0",
            "wake_quiet_seconds": 3,
            "sleep_quiet_seconds": 5,
            "sensors": [
                {
                    "name": "workshop",
                    "mac": "B8:06:0D:92:2F:5A",
                    "ip": "192.168.1.100",
                    "device_id": "device-id",
                    "local_key": "secret",
                    "version": 3.4,
                }
            ],
        }
        file_descriptor, path = tempfile.mkstemp()
        try:
            with os.fdopen(file_descriptor, "w") as config_file:
                json.dump(config_data, config_file)

            config = load_config(path)
        finally:
            os.unlink(path)

        self.assertEqual(config["interface"], "eth0")
        self.assertIn("b8:06:0d:92:2f:5a", config["sensors"])
        self.assertEqual(config["sensors"]["b8:06:0d:92:2f:5a"]["name"], "workshop")


if __name__ == "__main__":
    unittest.main()
