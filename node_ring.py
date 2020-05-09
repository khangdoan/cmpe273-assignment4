import hashlib
import math
from server_config import NODES
from pickle_hash import hash_code_hex, serialize
from bisect import bisect


def int2float(value):
    return (value & (0xFFFFFFFFFFFFFFFF >> (64 - 53))) / float(1 << 53)


class NodeRing():
    """
    Modified to accommodates Rendezvous Hashing and Consistent Hashing


    References:
        - Class Lecture Material
        - https://en.wikipedia.org/wiki/Rendezvous_hashing
        - https://en.wikipedia.org/wiki/Consistent_hashing
    """

    mode = None
    # weights holds all the weights corresponding to each node. nodes[i] -> weights[i]
    weights_rh = []
    seeds_rh = []
    replicas_ch = 0
    nodes_ch = []
    # store a list of sorted hash
    hashedNodeList = []
    vnodeMapping = {}

    def __init__(self, nodes, mode='Default', replicas=2):
        assert len(nodes) > 0
        self.nodes = nodes
        self.mode = mode
        if self.mode == 'Rendezvous Hashing':
            for i in range(len(nodes)):
                self.seeds_rh.append(i)
        elif self.mode == 'Consistent Hashing':
            self.replicas_ch = replicas
            # multiply the server nodes by the replication factor to get vnodes
            for node in self.nodes:
                for i in range(self.replicas_ch):
                    self.nodes_ch.append((node, i))

            for vnode in self.nodes_ch:
                hashedID = hash_code_hex(serialize(vnode))
                self.hashedNodeList.append(hashedID)
                self.vnodeMapping[hashedID] = vnode[0]
            self.hashedNodeList.sort()

    def get_node(self, key_hex):
        if self.mode == 'Consistent Hashing':
            return self.get_consistent_hash(key_hex)
        elif self.mode == 'Rendezvous Hashing':
            return self.get_rendezvous_hash(key_hex)
        else:
            return self.get_default_hash(key_hex)

    def get_default_hash(self, key_hex):
        key = int(key_hex, 16)
        node_index = key % len(self.nodes)
        return self.nodes[node_index]

    def get_consistent_hash(self, key_hex):
        # search the sorted list and if found
        index = bisect(self.hashedNodeList, key_hex)
        if index == len(self.hashedNodeList):
            return self.vnodeMapping[self.hashedNodeList[0]]
        else:
            return self.vnodeMapping[self.hashedNodeList[index]]

    @classmethod
    def get_score_rh(self, key, weight, seed):
        """get score function for redezvous hashing"""
        hashedKey = hash_code_hex((str(key) + str(seed)).encode())
        key = int2float(int(hashedKey, 16))
        score = 1.0 / (-math.log(key))
        return weight * score

    def get_rendezvous_hash(self, key):
        highScore, winner = -1, None
        for i in range(len(self.nodes)):
            score = self.get_score_rh(key,
                                      int(hash_code_hex(str(self.nodes[i].port).encode()), 16) % 5000, self.seeds_rh[i])
            if score > highScore:
                highScore, winner = score, self.nodes[i]
        return winner


def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))

# Uncomment to run the above local test via: python3 node_ring.py
# test()
