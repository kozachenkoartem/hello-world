import unittest

from leakguard.tuya_worker import WorkerManager, configure_device, create_device, emergency_shutdown, extract_dps


class FakeDevice(object):
    def __init__(self):
        self.version = None
        self.persistent = None
        self.retry_limit = None
        self.timeout = None

    def set_version(self, version):
        self.version = version

    def set_socketPersistent(self, value):
        self.persistent = value

    def set_socketRetryLimit(self, value):
        self.retry_limit = value

    def set_socketTimeout(self, value):
        self.timeout = value


class FakeTinyTuya(object):
    def __init__(self):
        self.arguments = None
        self.device = FakeDevice()

    def Device(self, device_id, address, local_key):
        self.arguments = (device_id, address, local_key)
        return self.device


class FakeWorker(object):
    instances = []

    def __init__(self, sensor, logger, window_seconds, retry_seconds, timeout_seconds):
        self.alive = False
        self.started = False
        self.stopped = False
        self.instances.append(self)

    def is_alive(self):
        return self.alive

    def start(self):
        self.alive = True
        self.started = True

    def stop(self):
        self.stopped = True


class FakeLogger(object):
    def __init__(self):
        self.messages = []

    def warning(self, message, sensor_name):
        self.messages.append((message, sensor_name))


class ExtractDpsTest(unittest.TestCase):
    def test_returns_dps_from_tuya_response(self):
        response = {"dps": {"1": "alarm", "3": "high"}}

        self.assertEqual(extract_dps(response), {"1": "alarm", "3": "high"})

    def test_ignores_tuya_response_without_dps(self):
        self.assertIsNone(extract_dps({"Error": "Device offline"}))

    def test_dry_run_shutdown_logs_alarm_without_controlling_pump(self):
        logger = FakeLogger()

        emergency_shutdown({"name": "workshop"}, logger)

        self.assertEqual(
            logger.messages,
            [("WATER LEAK %s - WOULD TURN PUMP OFF", "workshop")],
        )


class ConfigureDeviceTest(unittest.TestCase):
    def test_configures_short_persistent_connection(self):
        device = FakeDevice()

        configure_device(device, 3.4)

        self.assertEqual(device.version, 3.4)
        self.assertTrue(device.persistent)
        self.assertEqual(device.retry_limit, 1)
        self.assertEqual(device.timeout, 0.5)

    def test_creates_device_from_sensor_configuration(self):
        tinytuya = FakeTinyTuya()
        sensor = {
            "device_id": "device-id",
            "ip": "192.168.1.100",
            "local_key": "local-key",
            "version": 3.4,
        }

        device = create_device(sensor, tinytuya)

        self.assertIs(device, tinytuya.device)
        self.assertEqual(tinytuya.arguments, ("device-id", "192.168.1.100", "local-key"))
        self.assertEqual(device.version, 3.4)


class WorkerManagerTest(unittest.TestCase):
    def setUp(self):
        FakeWorker.instances = []

    def test_replaces_active_worker_on_new_wake_cycle(self):
        manager = WorkerManager(
            logger=None,
            window_seconds=20.0,
            retry_seconds=0.2,
            timeout_seconds=0.5,
            worker_factory=FakeWorker,
        )
        sensor = {"mac": "b8:06:0d:92:2f:5a"}

        self.assertTrue(manager.start(sensor))
        self.assertTrue(manager.start(sensor))
        self.assertTrue(FakeWorker.instances[0].stopped)


if __name__ == "__main__":
    unittest.main()
