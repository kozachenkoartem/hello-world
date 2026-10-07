# Leakguard Wake Detector

This service detects wake cycles of configured Wi-Fi leak sensors from
Ethernet frames. Each wake starts one bounded local TinyTuya worker to collect
and log received DPS. With `dry_run: false`, an alarm locally turns the pump
relay off through TinyTuya.

## Files

- `wake_listener.py`: Python 3.6-compatible AF_PACKET listener.
- `config.example.json`: public template. It contains no device identifiers or
  keys suitable for use.
- `config.json`: real local configuration. It is ignored by Git.
- `deploy.sh`: copies program files, never configuration, to Orange Pi.

## Deploy

From this directory, copy the current source files:

```sh
./deploy.sh kozak@192.168.1.124
```

On Orange Pi, create a real configuration once:

```sh
cd ~/leakguard-experiments/leakguard
cp config.example.json config.json
chmod 600 config.json
```

Edit `config.json` and replace the sensor `name` and `mac`. Do not copy a real
configuration back to this repository. `local_key` is used only for local Tuya
decryption and is never logged.

## Run

Raw Ethernet capture requires `CAP_NET_RAW`; for the prototype run it through
`sudo`:

```sh
cd ~/leakguard-experiments
sudo python3 -m leakguard.wake_listener --config leakguard/config.json
```

Expected log lines look like:

```text
19:50:44.123 INFO sensor workshop WAKE
19:50:49.123 INFO sensor workshop SLEEP
```

`wake_quiet_seconds` ends a wake cycle when a later packet from the same
sensor arrives after this quiet period. `sleep_quiet_seconds` produces `SLEEP`
when no later frame arrives. Initially use 3 and 5 seconds respectively; tune
them from the 10-cycle measurement.

## Local Tests

```sh
python3 -m unittest discover -s leakguard/tests -t . -v
```

## Wake-Cycle Test

1. Start the listener and leave it running.
2. Trigger ten separate physical sensor wakeups, waiting at least six seconds
   after the previous sensor traffic each time.
3. Record each physical wakeup and each `WAKE` line.
4. Stop with `Ctrl-C` and compare the two counts.

Set `dry_run: true` until the local relay shutdown path has been validated.
