# define MTU 1500

# from liyp.fattree import flow_to_classes

# class FlowGenerator:
#     def __init__(self, flow_size):
#         self.flow_size = flow_size

#     def size_dist(self):
#         packet_size = max(self.flow_size, MTU)
#         self.flow_size -= packet_size
#         return packet_size

from random import random
from unittest.util import _MAX_LENGTH
import numpy as np
import random


def generate_zipf(a, deadline):
    flow_size = np.random.zipf(a)
    r1 = random.randint(0, deadline - 1)
    return r1, flow_size

# for i in range(100):
#     print(generate_zipf(1.5, 100))

# if(__name__ == '__main__'):
    # a = 1.1
    # n = 10000

    # s = np.random.zipf(a, n)

    # print(s)

    # import matplotlib.pyplot as plt
    # from scipy.special import zeta

    # count = np.bincount(s, )
    # k = np.arange(1, s.max() + 1)

    # print(np.unique(s))

    # print(count)

    # plt.bar(k, count[1:], alpha=0.5, label='sample count')
    # plt.plot(k, n*(k**-a)/zeta(a), 'k.-', alpha=0.5,
    #         label='expected count')   
    # plt.semilogy()
    # plt.grid(alpha=0.4)
    # plt.legend()
    # plt.title(f'Zipf sample, a={a}, size={n}')
    # plt.show()