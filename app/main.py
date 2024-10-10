import json
import sys

import bencodepy
import hashlib

import requests
import struct
import socket

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"

bc = bencodepy.Bencode(encoding='utf-8')


def decode_torrent_file(torrent_file):
    with open(torrent_file, "rb") as file:
        torrent_data = file.read()

    result = []
    decoded_data = bencodepy.decode(torrent_data)
    tracker = decoded_data[b"announce"].decode('utf-8')
    length = decoded_data[b"info"][b"length"]
    sha = hashlib.sha1(bencodepy.encode(decoded_data[b'info'])).hexdigest()
    piece_length = decoded_data[b"info"][b'piece length']
    # print(decoded_data)
    print("Tracker URL:", tracker)
    print("Length:", length)
    print(f"Info Hash: {sha}")
    print(f"Piece Length: {piece_length}")
    print(f"Piece Hashes:")
    for i in range(0,len(decoded_data[b'info'][b'pieces']), 20):
        print(decoded_data[b'info'][b'pieces'][i:i+20].hex())
    return decoded_data

def getRequest(torrent_file):
    with open(torrent_file, 'rb') as file:
        bencoded_file = file.read()

    torrent_info = bencodepy.decode(bencoded_file)
    tracker_url = torrent_info[b'announce'].decode('utf-8')
    # sha = hashlib.sha1(bencodepy.encode(decoded_data[b'info'])).hexdigest()
    # print(torrent_info)
    query_params = dict(
        info_hash=hashlib.sha1(bencodepy.encode(torrent_info[b'info'])).digest(),
        peer_id = "00112233445566778899",
        port=6881,
        uploaded=0,
        downloaded=0,
        left=torrent_info[b'info'][b'length'],
        compact=1
    )

    response = bencodepy.decode(requests.get(tracker_url, query_params).content)
    # print(response)
    peers = response[b'peers']
    for i in range(0, len(peers), 6):
        peer = peers[i: i + 6]

        ip_address = f"{peer[0]}.{peer[1]}.{peer[2]}.{peer[3]}"

        port = int.from_bytes(peer[4:], byteorder="big", signed=False)

        print(f"{ip_address}:{port}")

def handshakeRequest(torrent_file, ip_port):
    ip, port = ip_port.split(":")
    with open(torrent_file, 'rb') as file:
        parsed = bencodepy.decode(file.read())
        info = parsed[b"info"]
        bencoded_info = bencodepy.encode(info)
        info_hash = hashlib.sha1(bencoded_info).digest()

        handshake = (
            b"\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00"
            + info_hash
            + b"00112233445566778899"
        )

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, int(port)))
            sock.send(handshake)
            print(f"Peer ID: {sock.recv(68)[48:].hex()}")

def decode_bencode(bencoded_value):
    return bc.decode(bencoded_value)


def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    elif command == "info":
        decoded_file = decode_torrent_file(sys.argv[2])

    elif command == "peers":
        getRequest(sys.argv[2])

    elif command == "handshake":
        handshakeRequest(sys.argv[2], sys.argv[3])

    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
