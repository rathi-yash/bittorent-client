# BitTorrent Client

## Cloning the Repository

To get started with this BitTorrent client, first clone the repository to your local machine:

```bash
git clone https://github.com/rathi-yash/bittorent-client.git
cd bittorrent-client
```

## Run :computer:

* Change directory to source in bittorrent folder and inorder to display help options 
```
    $ cd app
    $ python main.py --help
```

* Example for downloading torrent file given destination path for downloading file
```
    $ python main.py input_file.torrent -d destination_path/
```

* Example for seeding torrent file given destination path of existing file
```
    $ python main.py download ../sample.torrent ../

```

## Motivation 

* Downloading movies, music, games, or very large software is a popular activity using the **Bittorrent communication protocol**, which helps in distributing large chunks of data over the Internet. **One third of internet traffic contains Bittorrent data packets**, making it one of the most interesting and trending topics.

## Peer-to-Peer(P2P) Architecture

* The traditional client-server model is not scalable when many clients are requesting from a single server. This leads us to P2P architecture, where instead of a centralized server, peers or clients or end hosts participate in distributing data among themselves.

* Bittorrent is a protocol defined for sharing/exchange of data in peer-to-peer architecture, designed by **Bram Cohen**. The purpose of Bittorrent Protocol or BTP/1.0 was to achieve **advantages over plain HTTP when multiple downloads are possible**.

## Applications of Bittorrent

* Amazon Web Services(AWS) **Simple Storage Service**(S3) is a scalable internet-based storage service with an interface equipped with built-in Bittorrent.

* Facebook uses BitTorrent to distribute updates to Facebook servers.

* Open-source free software projects support their file sharing using Bittorrent to reduce load on servers. Example - Ubuntu ISO files.

* The Government of UK used Bittorrent to distribute the details of tax money spent by citizens.

**Fun Fact** - In 2011, BitTorrent had 100 million users and a greater share of network bandwidth than Netflix and Hulu combined.

## Bittorrent Client

* **Bittorrent protocol is an application layer protocol**, as it relies on the services provided by the lower 4 levels of the TCP/IP Internet model for sharing data. The Bittorrent Client is written at the application layer, following a set of rules or protocols to exchange data among peers (end hosts).

## Bittorrent File distribution process entities

| Entity Names      | Significance                                                                                              |
|-------------------|-----------------------------------------------------------------------------------------------------------|
| **.torrent file** | Contains details of trackers, file name, size, info hash, etc. regarding file being distributed           |
| **Tracker**       | Keeps state of the peers which are active in swarm and what part of files each peer has                   |
| **peers**         | End systems which may or may not have complete file but are participating in the file distribution        |
| **PWP**           | Protocol that end systems need to follow in order to distribute the file among other peers                |

* Peers participating in file sharing form a dense graph-like structure called a **swarm**. The peers are classified into two types: leechers (those who download only) and seeders (those who upload only).

* The large file being distributed is **divided into a number of pieces** which in turn are divided into a number of different chunks/blocks. The data chunks/blocks are actually shared among the peers, by which the whole file gets downloaded.

### Bittorrent tasks

* **Parsing .torrent**: Get .torrent file, read it and decode the bencoded information. Extract Tracker URLs, file size, name, piece length, info hash, files (if any), etc.

* **Tracker**: Communicate with the trackers to know which peers are participating in the download. The tracker response contains the peer information currently in the swarm.

* **PWP**: Peer Wire Protocol (PWP) is used to communicate with all the peers using peer wire messages (PWM) and download file pieces from the peers.

### Reading torrent files

* Files have extension .torrent and contain data about trackers URL, file name, file size, piece length, info hash and additional information about the file being distributed.

* Torrent files are bencoded, thus one requires parsing the torrent file and extracting the information about the original file being downloaded. The bittorrent client needs to write a parser for decoding torrent files.

* Torrent files can be generated for single/multiple files being distributed.

### Tracker

* Bittorrent client needs to know which peers are participating in the swarm for distributing the file. The Tracker is a server which keeps track of all the peers joining, leaving or currently active in the swarm.

* Tracker also knows how many seeders and leechers are present in the swarm for distributing a particular torrent file. However, note that the tracker doesn't actually have the torrent file.

#### HTTP/HTTPS trackers
* Trackers which use the HTTP protocol for responding with swarm information. 
* Client needs to do HTTP GET request to the tracker and receive HTTP response containing information about the swarm.
* This type of tracker introduces significant overhead when dealing with multiple clients at a time.

#### UDP trackers
* Trackers which use UDP protocol, optimized to provide less load on tracker servers.
* Since UDP is stateless and provides unreliable service, clients need to make multiple requests to the tracker.
* Client needs to communicate twice with the UDP tracker: once for connection ID and subsequently using that connectionID for announce request to get swarm information.

* Tracker URLs in torrent files can be absolute, so the client needs to communicate with all trackers unless it receives swarm data.

* A typical tracker response contains random 50 or fewer peers in the swarm along with some additional parameters.

## Peer Wire Protocol (PWP)

* According to BTP/1.0, PWP facilitates the exchange of file pieces. The Bittorrent Client maintains **state information** for each connection with a remote peer.

States            |  Significance
:----------------:|:-------------------------:
am choking        | client is choking the peer
peer choking      | peer is choking the client
am interested     | client interested in peer
peer interested   | peer interested in client

* Choking means the peer or client being choked will not receive messages for their requests until an unchoke message is received.

* Initial state of client for **downloading** will be **peer choking = 1** and **client interested = 0**, similarly for **uploading** the state will be **client choking = 1** and **peer interested = 0**. Communication with peers starts with these states using **Peer Wire Messages** (PWM).

### Peer Wire Messages

* All peer wire messages are sent over TCP connection, providing in-order and reliable bidirectional data communication.

Message           |  Significance
:----------------:|:-------------------------:
handshake         | Initial message to be shared after TCP connection
keep alive        | Message indicating that the peer connection is still active
choke             | Peer is choking client
unchoke           | Peer is unchoking client
interested        | Peer is interested in client
uninterested      | Peer is uninterested in client
bitfield          | Pieces that peer has
have              | Piece that peer has
request           | Request for piece to peer
piece             | Piece data response from peer

* The ideal sequence of message exchange after establishing a successful TCP connection is as follows:

|Message Sequence |   Client side     |     to/from      |    Peer side        |
|-----------------|-------------------|------------------|---------------------|
|1                | Handshake request |      --->        |                     |
|2                |                   |      <---        | Handshake response  |
|3                |                   |      <---        | Bitfield            |
|4                |                   |      <---        | Have(optional)      |
|5                | Interested        |      --->        |                     |
|6                |                   |      <---        | Unchoke/Choke       |
|7                | Request1          |      --->        |                     |
|8                |                   |      <---        | Piece1              |
|9                | Request2          |      --->        |                     |
|10               |                   |      <---        | Piece2              |
|k                | ...               |      --->        |                     |
|k + 1            |                   |      <---        | ...                 |

* To handle various issues and timeouts, a Downloading Finite State Machine is designed, taking into consideration the order of message exchange and client state.

## Legal issues with BitTorrent

* Torrenting itself is legal! It's a protocol used in peer-to-peer architecture. The problem lies in the content shared on torrent, which needs to be monitored and must have permission from the owner to share.

* Downloading copyrighted content like new Netflix web series, movies, songs, or gaming software is illegal and can lead to legal issues. It's challenging to monitor copyrighted bittorrent traffic over the internet.

* Ensure that whatever you download via Bittorrent doesn't have such issues, and enjoy legal torrenting!

