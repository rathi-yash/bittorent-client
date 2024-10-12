import hashlib
import bencodepy
import binascii
import requests
import struct
import ipaddress
import math
import socket
from decoder import Decoder
from message_ids import MessageIDs
import os


class TorrentClient:

    def __init__(self) -> None:
        self.decoder = Decoder()

    def fetch_torrent_info(self, file_name):

        if not file_name:
            raise ValueError("Invalid file path")

        with open(file_name, 'rb') as f:

            read_data = f.read()

            torrent_info_dict = Decoder().decode_bencoded_value(read_data)

            torrent_info = Decoder().decode_bencode(read_data)

            piece_length = torrent_info_dict.get('info').get('piece length')

            pieces = torrent_info.get('info').get('pieces')

            piece_hashes = [pieces[i:i + 20] for i in range(0, len(pieces), 20)]

            piece_hashes_in_hex = [binascii.hexlify(piece).decode() for piece in piece_hashes]

            if 'info' not in torrent_info:
                raise ValueError("Invalid torrent file: 'info' field is missing")

            start_index = read_data.index(b'4:info') + 6

            end_index = start_index + len(bencodepy.encode(torrent_info['info']))

            raw_info_dict = read_data[start_index:end_index]

            info_hash = hashlib.sha1(raw_info_dict).hexdigest()

            tracker_url = torrent_info_dict['announce']

            torrent_length = torrent_info_dict['info']['length']

            print(f"Tracker URL: {tracker_url}")

            print(f"Length: {torrent_length}")

            print(f"Info Hash: {info_hash}")

            print(f"Piece Length: {piece_length}")

            print("Piece Hashes:")

            for piece_hash in piece_hashes_in_hex:
                print(piece_hash)

            return hashlib.sha1(raw_info_dict), tracker_url, torrent_length, piece_length, len(piece_hashes_in_hex)

    def fetch_peer_info(self, torrent_file):

        peers = []

        info_hash, tracker_url, torrent_length, pl, l = self.fetch_torrent_info(torrent_file)

        peer_id = '00112233445566778897'  # random value of peer_id

        uploaded = 0

        downloaded = 0

        parsed_hash = info_hash.digest()

        params = {

            'info_hash': parsed_hash,

            'peer_id': peer_id,

            'port': 6881,

            'uploaded': uploaded,

            'downloaded': downloaded,

            'left': torrent_length,

            'compact': 1

        }

        raw_resp = requests.get(url=tracker_url, params=params)

        peers_bytes = self.decoder.decode_bencode(raw_resp.content).get('peers')

        peers = [peers_bytes[i:i + 6] for i in range(0, len(peers_bytes), 6)]

        res = []

        for p in peers:
            ip, port = struct.unpack('!IH', p)

            ip = ipaddress.ip_address(ip)

            res.append(f'{ip}:{port}')

        for r in res:
            print(r)

        return res

    def recieve_data(sefl, soc):

        length = b''

        while not length or not int.from_bytes(length, 'big'):
            length = soc.recv(4)

        length = int.from_bytes(length, 'big')

        data = soc.recv(length)

        while len(data) < length:
            data += soc.recv(length)

        message_id = int.from_bytes(data[:1], 'big')

        payload = data[1:]

        return message_id, payload

    def get_peer_id(self, torrent_file, peer_ip_and_port):

        ip, port = peer_ip_and_port.split(':')

        info_hash, tracker_url, torrent_length, piece_length, num_pieces = self.fetch_torrent_info(torrent_file)

        bit_protocol_req = bytearray()

        bit_protocol_req.extend([19])

        bit_protocol_req.extend('BitTorrent protocol'.encode())

        for _ in range(8):
            bit_protocol_req.extend([0])

        bit_protocol_req.extend(info_hash.digest())

        bit_protocol_req.extend('00112233445566778899'.encode())  # peer_id

        pid = ''

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, int(port)))

            s.sendall(bit_protocol_req)

            # Receive the handshake response

            data = s.recv(1024)

            pid = data[-20:]

            return binascii.hexlify(pid).decode()

    def wait_for_peer_messag(self, soc, message_id):

        reciveved_id, data = self.recieve_data(soc)

        while message_id != reciveved_id:
            reciveved_id, data = self.recieve_data(soc)

        return data

    def wait_for_unchoke(self, soc):

        return self.wait_for_peer_messag(soc, MessageIDs.UNCHOKE)

    def wait_for_bitfield(self, soc):

        return self.wait_for_peer_messag(soc, MessageIDs.BITFIELD)

    def get_block(self, soc, index, begin, block_length):

        request_message = b'\x00\x00\x00\x0d\x06'

        request_message += index.to_bytes(4, byteorder='big')

        request_message += begin.to_bytes(4, byteorder='big')

        request_message += block_length.to_bytes(4, byteorder='big')

        soc.sendall(request_message)

        messageid, recieved_block_content = self.recieve_data(soc)

        return recieved_block_content[8:]

    def send_interested_message(self, soc):

        request_message = b'\x00\x00\x00\x01\x02'

        soc.sendall(request_message)

    def download_piece(self, torrent_file: str, peer_ip_and_port: str, piece_index: int, output_file: str):

        ip, port = peer_ip_and_port.split(':')

        block_length = 16 * 1024

        info_hash, tracker_url, torrent_length, piece_length, num_pieces = self.fetch_torrent_info(torrent_file)

        bit_protocol_req = bytearray()

        bit_protocol_req.extend([19])

        bit_protocol_req.extend('BitTorrent protocol'.encode())

        for _ in range(8):
            bit_protocol_req.extend([0])

        bit_protocol_req.extend(info_hash.digest())

        bit_protocol_req.extend('00112233445566778899'.encode())

        piece_data = bytearray()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.connect((ip, int(port)))

            s.sendall(bit_protocol_req)

            d = s.recv(68)  # Handshake

            bitfield = self.wait_for_bitfield(s)

            self.send_interested_message(s)

            # recieve unchoke

            unchoke_message = self.wait_for_unchoke(s)

            if piece_index == num_pieces - 1:

                piece_length = (torrent_length % piece_length) or piece_length

            else:

                piece_length = piece_length

            number_of_blocks = math.ceil(piece_length / block_length)

            for block_index in range(number_of_blocks):

                if block_index == number_of_blocks - 1:  # This is the last block

                    offset = piece_length - min(block_length, piece_length - block_length * block_index)

                else:

                    offset = block_length * block_index

                bl = min(block_length, piece_length - offset)

                block_data = self.get_block(s, piece_index, offset, bl)

                piece_data.extend(block_data)

            # Send have message

            have_message = b'\x00\x00\x00\x05\x04'

            have_message += piece_index.to_bytes(4, byteorder='big')

            s.sendall(have_message)

        with open(output_file, 'wb') as f:

            f.write(piece_data)

        return piece_data

    def download_torrent_file(self, torrent_file: str, output_file: str):
        info_hash, tracker_url, torrent_length, piece_length, num_pieces = self.fetch_torrent_info(torrent_file)
        peer_ips = self.fetch_peer_info(torrent_file)
        peer_ip = peer_ips[0]
        torrent = bytearray()

        print(f"Downloading {torrent_file} to {output_file}")
        print(f"Total pieces: {num_pieces}")

        for piece_index in range(num_pieces):
            print(f"Downloading piece {piece_index + 1}/{num_pieces}")
            piece_data = self.download_piece(torrent_file, peer_ip, piece_index, f"{output_file}.part{piece_index}")
            torrent.extend(piece_data)

        with open(output_file, 'wb') as f:
            f.write(torrent)

        # Clean up temporary files
        for piece_index in range(num_pieces):
            os.remove(f"{output_file}.part{piece_index}")

        print(f"Download complete: {output_file}")
