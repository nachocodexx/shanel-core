# * This block of code MUST be executed first.  
# _______________________________________________________
import os
import sys
from pathlib import Path
import time

path_root      = Path(__file__).parent.absolute()
(path_root, _) = os.path.split(path_root)
sys.path.append(str(path_root))
# ______________________________________________________
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor,wait
import unittest

from clustering.secure.skmeans import SKMeans
from clustering.secure.dbskmeans import Dbskmeans
from clustering.secure.dbsnnc import Dbsnnc

from security.cryptosystem.liu import Liu
from security.cryptosystem.dataowner import DataOwner
from security.cryptosystem.FDHOpe import Fdhope

from utils.Utils import Utils
from utils.constants import Constants

liu        = Liu(round = True)        
m          = 3
k          = 3
sk         = liu.secretKey( m = m )
plaintext_matrix = [
    [0.73,8.84],
    [49.93,34.44],
    [0.57,65.04],
    [62.15,32.29],
    [59.47,36.04]
]


class TestCore(unittest.TestCase):
    

    def test_outsourcednnc(self):
        dow0 = DataOwner(
            m = m,
            liu_scheme = liu,
        )
        outsourced = dow0.outsourceDataDbsnnc(
            plaintext_matrix = plaintext_matrix,
            threshold = 10
        )

        dbsnnc, label_vector = Dbsnnc.run(
            ciphertext_matrix = outsourced.encrypted_matrix,
            EDM = outsourced.UDM,
            encrypted_threshold = outsourced.encrypted_threshold,
        )
        print(dbsnnc, label_vector)
    
    @unittest.skip("")
    def test_nncData(self):
        dow0 = DataOwner(
            m = m,
            liu_scheme = liu,
        )
        D = [[-3,3],[-2,3],[-3,2],[-2,2],[2,3], [3,3], [2,2], [3,2],[-3,-2],[-3,-3],[-2,-3],[-2,-2],[2,-3],[3,-3],[2,-2],[3,-2]]

        outsourced = dow0.outsourceDataDbsnnc(
            plaintext_matrix = D,
            threshold = 1
        )

        print("D1",outsourced.encrypted_matrix)
        print("ED",outsourced.UDM)
        print("Threshold",outsourced.encrypted_threshold)

        
    @unittest.skip("")
    def test_outsourcedbskmeans(self):
        dow0 = DataOwner(
            m = m,
            liu_scheme = liu,
        )
        outsourced = dow0.outsourceDataDBS(
            plaintext_matrix = plaintext_matrix
        )

        print(outsourced.messageIntervals)
        print(outsourced.cypherIntervals)


if __name__ == '__main__':
    unittest.main()
