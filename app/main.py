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

    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
