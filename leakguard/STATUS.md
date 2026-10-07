# Leakguard Status

## Current Deployment

- Orange Pi service: `leakguard.service`.
- Service is enabled for `multi-user.target` and runs as user `kozak`.
- The service has only `CAP_NET_RAW`; it is not a root Python process.
- Runtime directory: `~/leakguard-experiments/leakguard/`.
- Real configuration: `config.json`, owner `kozak`, mode `0600`, not in Git.
- Service logs: `sudo journalctl -u leakguard.service`.

## Implemented Flow

1. AF_PACKET listens on `eth0` for configured sensor source MAC addresses.
2. A sensor ARP frame triggers a wake event.
3. The current sensor IP is read from the ARP sender address, so configured
   static IP values are fallback only.
4. A bounded TinyTuya 3.4 worker connects locally and receives DPS updates.
5. `DPS 1 = alarm` invokes the emergency path.
6. With `dry_run = true`, the emergency path only logs its intended action.
7. With `dry_run = false`, it sends local TinyTuya `turn_off()` to the pump
   relay. There is no `turn_on()` path.

## Verified Behavior

- Both configured water leak sensors produced local `WAKE`, `LOCAL CONNECTED`,
  and `DPS {"1":"alarm"}` events.
- `DPS 1 = normal` was observed after drying.
- Dry-run logging was verified for both sensors.
- Live pump relay shutdown was verified from a sensor alarm. Journal contained
  `WATER LEAK <sensor> - PUMP TURNED OFF`.

## Operations

Deploy source files without copying secrets:

```sh
./leakguard/deploy.sh kozak@192.168.1.124
```

After changing the local real config, copy it manually to the runtime
directory, set mode `0600`, then restart the service:

```sh
sudo systemctl restart leakguard.service
sudo systemctl status leakguard.service
```

Do not commit `config.json`, local keys, device IDs, or relay credentials.
