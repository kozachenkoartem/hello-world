import argparse
import json
import logging
import select
import socket
import time

from leakguard.tuya_worker import WorkerManager, configure_emergency

ETH_P_ALL = 0x0003
LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s"


class WakeTracker(object):
    def __init__(self, sensors, wake_quiet_seconds, sleep_quiet_seconds):
        self._sensors = sensors
        self._wake_quiet_seconds = wake_quiet_seconds
        self._sleep_quiet_seconds = sleep_quiet_seconds
        self._active_macs = set()
        self._last_seen = {}

    def on_packet(self, mac, now):
        sensor = self._sensors.get(mac)
        if sensor is None:
            return []

        events = []
        if mac in self._active_macs and now - self._last_seen[mac] >= self._wake_quiet_seconds:
            self._active_macs.remove(mac)
            events.append(("SLEEP", sensor["name"]))

        self._last_seen[mac] = now
        if mac in self._active_macs:
            return events

        self._active_macs.add(mac)
        events.append(("WAKE", sensor["name"]))
        return events

    def collect_sleep_events(self, now):
        events = []
        for mac in list(self._active_macs):
            if now - self._last_seen[mac] < self._sleep_quiet_seconds:
                continue

            self._active_macs.remove(mac)
            events.append(("SLEEP", self._sensors[mac]["name"]))
        return events


def source_mac(frame):
    if len(frame) < 12:
        return None
    return ":".join("{:02x}".format(byte) for byte in frame[6:12])


def arp_sender_ip(frame):
    if len(frame) < 42 or frame[12:14] != b"\x08\x06":
        return None
    return socket.inet_ntoa(frame[28:32])


def load_config(path):
    with open(path, "r") as config_file:
        config = json.load(config_file)

    interface = config.get("interface")
    if not isinstance(interface, str) or not interface:
        raise ValueError("config.interface must be a non-empty string")

    sensors = config.get("sensors")
    if not isinstance(sensors, list) or not sensors:
        raise ValueError("config.sensors must be a non-empty list")

    sensors_by_mac = {}
    for sensor in sensors:
        if not isinstance(sensor, dict):
            raise ValueError("each sensor must be an object")
        name = sensor.get("name")
        mac = sensor.get("mac")
        if not isinstance(name, str) or not name:
            raise ValueError("sensor.name must be a non-empty string")
        if not isinstance(mac, str) or len(mac.split(":")) != 6:
            raise ValueError("sensor.mac must be a MAC address")

        normalized_mac = mac.lower()
        if normalized_mac in sensors_by_mac:
            raise ValueError("sensor.mac values must be unique")
        sensor["mac"] = normalized_mac
        sensors_by_mac[normalized_mac] = sensor

    config["sensors"] = sensors_by_mac
    config.setdefault("wake_quiet_seconds", 3.0)
    config.setdefault("sleep_quiet_seconds", 5.0)
    config.setdefault("worker_window_seconds", 20.0)
    config.setdefault("worker_retry_seconds", 0.2)
    config.setdefault("worker_connect_timeout_seconds", 0.5)
    config.setdefault("debug", False)
    config.setdefault("dry_run", True)
    if (
        config["wake_quiet_seconds"] <= 0
        or config["sleep_quiet_seconds"] <= 0
        or config["worker_window_seconds"] <= 0
        or config["worker_retry_seconds"] <= 0
        or config["worker_connect_timeout_seconds"] <= 0
    ):
        raise ValueError("quiet periods must be greater than zero")
    if not config["dry_run"] and not isinstance(config.get("pump"), dict):
        raise ValueError("config.pump is required when dry_run is false")
    return config


def log_events(events, logger):
    for event, sensor_name in events:
        logger.info("sensor %s %s", sensor_name, event)


def run(config, logger):
    configure_emergency(config.get("pump"), config.get("dry_run", True))
    tracker = WakeTracker(
        sensors=config["sensors"],
        wake_quiet_seconds=config["wake_quiet_seconds"],
        sleep_quiet_seconds=config["sleep_quiet_seconds"],
    )
    worker_manager = WorkerManager(
        logger=logger,
        window_seconds=config["worker_window_seconds"],
        retry_seconds=config["worker_retry_seconds"],
        timeout_seconds=config["worker_connect_timeout_seconds"],
    )
    raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
    raw_socket.bind((config["interface"], 0))
    logger.info("listening on %s for %d configured sensor(s)", config["interface"], len(config["sensors"]))

    try:
        while True:
            ready_sockets, _, _ = select.select([raw_socket], [], [], 0.25)
            now = time.monotonic()
            if ready_sockets:
                frame = raw_socket.recv(65535)
                mac = source_mac(frame)
                if mac is not None:
                    events = tracker.on_packet(mac, now)
                    log_events(events, logger)
                    if any(event == "WAKE" for event, _ in events):
                        sensor = dict(config["sensors"][mac])
                        current_ip = arp_sender_ip(frame)
                        if current_ip is not None:
                            sensor["ip"] = current_ip
                        worker_manager.start(sensor)
            log_events(tracker.collect_sleep_events(now), logger)
    finally:
        raw_socket.close()


def main():
    parser = argparse.ArgumentParser(description="Tuya leak sensor wake detector")
    parser.add_argument("--config", default="config.json", help="path to JSON configuration")
    arguments = parser.parse_args()

    config = load_config(arguments.config)
    logging.basicConfig(
        level=logging.DEBUG if config["debug"] else logging.INFO,
        format=LOG_FORMAT,
        datefmt="%H:%M:%S",
    )
    try:
        run(config, logging.getLogger("leakguard"))
    except KeyboardInterrupt:
        logging.getLogger("leakguard").info("stopped")


if __name__ == "__main__":
    main()
