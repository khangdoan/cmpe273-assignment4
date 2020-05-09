import math
from pickle_hash import hash_code_hex


def getArraySize(items_count: int, falsepos_prob: float) -> int:
    # Formula used for array size calculation
    #  size = -(items_count * log(falsePos_prob)) / (log(2) ^ 2)
    return int(-(items_count * math.log(falsepos_prob)) / math.log(2) ** 2)


def getHashCount(array_size: int, items_count: int) -> int:
    # Calculation based on the following formula
    # Hash Count = (array_size/item_count) * log(2)
    return int((array_size / items_count) * math.log(2))


def hashFunc(id: str, seed: str):
    print(hash_code_hex((id + seed).endcode()))


class BloomFilter:
    """
    This implementation is based on the calculation of the most optimal hash function based on the input:
    - number of item to be stored
    - probability of false positive

    Reference:
    - https://en.wikipedia.org/wiki/Bloom_filter
    """
    falsePos_prob = None
    item_num = None
    # used list of true,false, instead of bitarray lib
    bitArray = []
    arraySize = None
    numOfHash = None

    def __init__(self, item_cnts, falsePos_prob):
        self.falsePos_prob = falsePos_prob
        self.arraySize = getArraySize(item_cnts, falsePos_prob)
        self.numOfHash = getHashCount(self.arraySize, item_cnts)
        # initilizing array with all false
        for i in range(0, self.arraySize):
            self.bitArray.append(False)

    def add(self, item: str):
        for i in range(0, self.numOfHash):
            index = int(hash_code_hex((item + str(i)).encode()), 16) % self.arraySize
            self.bitArray[index] = True

    def is_member(self, item: str):
        for i in range(self.numOfHash):
            if self.bitArray[int(hash_code_hex((item + str(i)).encode()), 16) % self.arraySize] is False:
                return False
        return True
