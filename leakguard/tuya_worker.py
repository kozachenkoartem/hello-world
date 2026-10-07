import json
import threading
import time

_pump = None
_dry_run = True


def configure_emergency(pump, dry_run):
    global _pump, _dry_run
    _pump = pump
    _dry_run = dry_run


def emergency_shutdown(sensor, logger):
    if _dry_run:
        logger.warning("WATER LEAK %s - WOULD TURN PUMP OFF", sensor["name"])
        return
    import tinytuya
    pump = create_device(_pump, tinytuya)
    pump.turn_off()
    logger.warning("WATER LEAK %s - PUMP TURNED OFF", sensor["name"])


def extract_dps(response):
    if not isinstance(response, dict):
        return None
    dps = response.get("dps")
    if not isinstance(dps, dict):
        return None
    return dps


def configure_device(device, version, timeout_seconds=0.5):
    device.set_version(version)
    device.set_socketPersistent(True)
    device.set_socketRetryLimit(1)
    device.set_socketTimeout(timeout_seconds)


def create_device(sensor, tinytuya_module, timeout_seconds=0.5):
    device = tinytuya_module.Device(
        sensor["device_id"], sensor["ip"], sensor["local_key"]
    )
    configure_device(device, sensor["version"], timeout_seconds)
    return device


class SensorWorker(threading.Thread):
    def __init__(self, sensor, logger, window_seconds, retry_seconds, timeout_seconds):
        threading.Thread.__init__(self, name="leakguard-" + sensor["name"])
        self.daemon = True
        self._sensor = sensor
        self._logger = logger
        self._window_seconds = window_seconds
        self._retry_seconds = retry_seconds
        self._timeout_seconds = timeout_seconds
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def _log_response(self, response):
        dps = extract_dps(response)
        if dps is not None:
            self._logger.info(
                "sensor %s DPS %s",
                self._sensor["name"],
                json.dumps(dps, sort_keys=True, separators=(",", ":")),
            )
            if dps.get("1") == "alarm":
                emergency_shutdown(self._sensor, self._logger)

    def run(self):
        import tinytuya

        deadline = time.monotonic() + self._window_seconds
        while not self._stop_event.is_set() and time.monotonic() < deadline:
            device = None
            try:
                device = create_device(self._sensor, tinytuya, self._timeout_seconds)
                response = device.status(nowait=True)
                if device.socket is None:
                    time.sleep(self._retry_seconds)
                    continue

                self._logger.info("sensor %s LOCAL CONNECTED", self._sensor["name"])
                self._log_response(response)
                while not self._stop_event.is_set() and time.monotonic() < deadline:
                    response = device.receive()
                    self._log_response(response)
                    if response is None:
                        device.heartbeat(nowait=True)
                return
            except Exception as error:
                self._logger.debug("sensor %s local attempt failed: %s", self._sensor["name"], error)
                time.sleep(self._retry_seconds)
            finally:
                device_socket = getattr(device, "socket", None)
                if device_socket is not None:
                    device_socket.close()
                    device.socket = None


class WorkerManager(object):
    def __init__(
        self,
        logger,
        window_seconds,
        retry_seconds,
        timeout_seconds,
        worker_factory=SensorWorker,
    ):
        self._logger = logger
        self._window_seconds = window_seconds
        self._retry_seconds = retry_seconds
        self._timeout_seconds = timeout_seconds
        self._worker_factory = worker_factory
        self._workers = {}

    def start(self, sensor):
        existing_worker = self._workers.get(sensor["mac"])
        if existing_worker is not None and existing_worker.is_alive():
            existing_worker.stop()

        worker = self._worker_factory(
            sensor,
            self._logger,
            self._window_seconds,
            self._retry_seconds,
            self._timeout_seconds,
        )
        self._workers[sensor["mac"]] = worker
        worker.start()
        return True
