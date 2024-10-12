import sys
import json
from commands import Commands
from decoder import Decoder
from torrent_client import TorrentClient
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [arguments]")
        sys.exit(1)

    command = sys.argv[1]
    bencoded_decoder = Decoder()
    torrent_client = TorrentClient()

    if command == Commands.DECODE:
        bencoded_value = sys.argv[2].encode()
        print(json.dumps(bencoded_decoder.decode_bencoded_value(bencoded_value)))
    elif command == Commands.INFO:
        file_name = sys.argv[2]
        torrent_client.fetch_torrent_info(file_name)
    elif command == Commands.PEERS:
        file_name = sys.argv[2]
        torrent_client.fetch_peer_info(file_name)
    elif command == Commands.HANDSHAKE:
        file_name = sys.argv[2]
        peer = sys.argv[3]
        peer_id = torrent_client.get_peer_id(file_name, peer)
        print(f'Peer ID: {peer_id}')
    elif command == Commands.DOWNLOAD_PIECE:
        output_file = sys.argv[3]
        torrent_file = sys.argv[4]
        piece_number = sys.argv[5]
        peer_ip = torrent_client.fetch_peer_info(torrent_file)[0]
        result = torrent_client.download_piece(torrent_file, peer_ip, int(piece_number), output_file)
        print(f'Piece {piece_number} downloaded to {output_file}.')
    elif command == Commands.DOWNLOAD:
        if len(sys.argv) < 4:
            print("Usage: python main.py download <torrent_file> <destination_directory>")
            sys.exit(1)

        torrent_file = sys.argv[2]
        destination_directory = sys.argv[3]

        # Extract the file name from the torrent file
        with open(torrent_file, 'rb') as f:
            torrent_data = f.read()
            torrent_info = Decoder().decode_bencoded_value(torrent_data)
            file_name = torrent_info['info']['name']

        # Combine destination directory with file name
        output_file = os.path.join(destination_directory, file_name)

        # Ensure the destination directory exists
        os.makedirs(destination_directory, exist_ok=True)

        torrent_client.download_torrent_file(torrent_file, output_file)
        print(f'Downloaded {torrent_file} to {output_file}.')
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
