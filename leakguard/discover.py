import socket
import time


def mac_address(frame):
    return ":".join("{:02x}".format(value) for value in frame[6:12])


def main():
    raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    raw_socket.bind(("eth0", 0))
    raw_socket.settimeout(0.5)
    deadline = time.monotonic() + 90.0
    print("discovery started", flush=True)
    try:
        while time.monotonic() < deadline:
            try:
                frame = raw_socket.recv(65535)
            except socket.timeout:
                continue
            if len(frame) < 42:
                continue
            source_mac = mac_address(frame)
            ethernet_type = frame[12:14]
            if ethernet_type == b"\x08\x06":
                sender_ip = socket.inet_ntoa(frame[28:32])
                print("ARP mac={} ip={}".format(source_mac, sender_ip), flush=True)
            elif ethernet_type == b"\x08\x00" and frame[23] == 6:
                ip_header_length = (frame[14] & 0x0f) * 4
                tcp_offset = 14 + ip_header_length
                if len(frame) >= tcp_offset + 4:
                    destination_port = int.from_bytes(frame[tcp_offset + 2:tcp_offset + 4], "big")
                    if destination_port == 8883:
                        source_ip = socket.inet_ntoa(frame[26:30])
                        destination_ip = socket.inet_ntoa(frame[30:34])
                        print("MQTT mac={} {} -> {}:8883".format(source_mac, source_ip, destination_ip), flush=True)
    finally:
        raw_socket.close()


if __name__ == "__main__":
    main()
