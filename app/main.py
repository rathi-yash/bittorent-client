import json
import sys

import bencodepy
import hashlib

# import requests - available if you need it!

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"

bc = bencodepy.Bencode(encoding='utf-8')


def decode_torrent_file(torrent_file):
    with open(torrent_file, "rb") as file:
        torrent_data = file.read()

    decoded_data = bencodepy.decode(torrent_data)
    tracker = decoded_data[b"announce"].decode('utf-8')
    length = decoded_data[b"info"][b"length"]
    sha = hashlib.sha1(bencodepy.encode(decoded_data[b'info'])).hexdigest()
    return tracker, length, sha


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
        torr_tracker, torr_length, sha = decode_torrent_file(sys.argv[2])
        print("Tracker URL:", torr_tracker)
        print("Length:", torr_length)
        print(f"Info Hash: {sha}")
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
