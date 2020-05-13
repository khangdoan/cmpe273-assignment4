import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
# from LRUCache import LRUCache
from bloom_filter import BloomFilter
# from lru_cache import lru_cache
# >>>>UNCOMMENT BELOW TO TEST FOR 10,000 USER<<<
# from sample_data_10000 import USERS

BUFFER_SIZE = 1024

bloomfilter = BloomFilter(1000, 0.001)

shard_counts = {'4000': 0,
                '4001': 0,
                '4002': 0,
                '4003': 0}

class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()


# @lru_cache(5)
def get(id, clientRing):
    data, key = serialize_GET(id)
    if bloomfilter.is_member(key):
        return clientRing.get_node(key).send(data)
    else:
        return None


# @lru_cache(5)
def put(object, clientRing):
    data, key = serialize_PUT(object)
    bloomfilter.add(key)
    # *********added diagnostic code to see sharding distribution********
    retval = clientRing.get_node(key,data)
    global shard_counts
    shard_counts[str(retval.port)] = shard_counts[str(retval.port)]+1
    return retval.send(data)


# @lru_cache(5)
def delete(id, clientRing):
    data, key = serialize_DELETE(id)
    if bloomfilter.is_member(key):
        return clientRing.get_node(key).send(data)
    else:
        return None


def process(udp_clients, client_ring=None):
    if client_ring is None:
        client_ring = NodeRing(udp_clients)

    hash_codes = set()
    # PUT all users.
    for u in USERS:
        response = put(u, client_ring)
        print(response)
        hash_codes.add(str(response.decode()))
    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    # GET all users.
    for hc in hash_codes:
        print(hc)
        response = get(hc,client_ring)
        print(response)

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    ###########################Test Code################################
    ch_rh = []
    # global shard_counts
    client_ring_CH = NodeRing(clients,mode='Consistent Hashing', replicas=8)
    client_ring_RH = NodeRing(clients, mode='Rendezvous Hashing')
    for c in [client_ring_CH, client_ring_RH]:
        process(clients, c)
        temp = c.mode, {i: shard_counts[i] for i in shard_counts}
        ch_rh.append(temp)
        for i in shard_counts:
            shard_counts[i] = 0
    print("******************Server Distribution:**************")
    for i in ch_rh:
        print(i)
    ####################################################################
