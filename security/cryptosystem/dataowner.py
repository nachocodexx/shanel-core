import numpy as np
from utils.Utils import Utils

"""
Description:
    A class that represents the preparation step, performed by data owners, 
    to securely externalize their data to the TPDM that provides DMaaS.

Attributes:
	m: int   - constraints [ m >= 3 ]
        Number of attributes of SK
	liu_schema: Liu <object>
		represent a symmetric encryption scheme
"""

class DataOwner(object):

    def __init__(self,**kwargs):
        m               = kwargs.get("m")
        liu_scheme      = kwargs.get("liu_scheme")
        self.m          = m 
        self.liu_scheme = liu_scheme
        self.sk         = self.liu_scheme.secretKey( m = self.m )

    def setM(self,m):
        self.m = m


    """
    description: Data preparation.
    attributes: 
        rawD: original dataset
        D: numeric dataset
        a: number of attributes of D
        m: number of attributes of SK
    """
    def outsourcedData(self,**kwargs):
        # ____________
        #   Transform: rawD -> D(numeric) 
        # ___________
        D      = kwargs.get("plaintext_matrix",[[]])
        Dshape = Utils.getShapeOfMatrix(D)
        a = kwargs.get("attributes",  Dshape[1] )
        # D1: ciphertext_matrix, U: UDM  
        D1 = self.liu_scheme.encryptMatrix(
            plaintext_matrix = D,
            secret_key       = self.sk,
            m                = self.m
        )
        U  = Utils.create_UDM(plaintext_matrix = D)
        return D1,U


    """
    description: dataowner participation for shift matrix decryption
    attributes:
        S1: shift matrix
        m: number of attributes of SK
    """
    def userActions(self,**kwargs):
        # __________________________________
        S1 = kwargs.get("shift_matrix",[])
        m  = kwargs.get("m",3)
        # ___________________________________
        S  = self.liu_scheme.decryptMatrix(
            ciphertext_matrix = S1,
            secret_key        = self.sk,
            m                 = self.m
        )
        return S

    """
    description: decrypt final clusters
    attributes:
        cipher_cluster: set of encrypted clusters
        m: number of attributes of SK
    """
    def verify(self,**kwargs):
        cipher_clusters = kwargs.get("cipher_clusters") 
        Ss              = []
        for cipher_cluster in cipher_clusters:
            S  = self.liu_scheme.decryptMatrix(
                ciphertext_matrix = cipher_cluster,
                secret_key        = self.sk,
                m                 = self.m
            )
            Ss.append(S)
        return Ss
