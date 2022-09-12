import numpy as np
from utils.Utils import Utils

"""
Description: 
	A class	to a class that represents the preparation step, performed by data owners, 
    to securely externalize their data to the TPDM that provides DMaaS.

Attributes:
	m: int   - constraints [ m >= 3 ]
        Number of attributes of SK
	liu_schema: Liu <object>
		represent a symmetric encryption scheme
	fdh_ope: 
		represents the Frequency and Distribution Hiding OPE (FDH-OPE) 
		scheme to facilitate operations for UDM.
"""
class DataOwner:

	def __init__(self, **kwargs):
		m               = kwargs.get("m")
		liu_scheme      = kwargs.get("liu_scheme")
		fdh_ope         = kwargs.get("fdh_ope")
		self.m          = m 
		self.liu_scheme = liu_scheme
		self.sk         = self.liu_scheme.secretKey( m = self.m )
		self.messageIntervals, self.cypherIntervals = [], []


	"""
    description: Data preparation.
    attributes: 
        rawD: original dataset
        D: numeric dataset
        a: number of attributes of D
        m: number of attributes of SK
    """
	def outsourceData(self, **kwargs): 
		D      = kwargs.get("plaintext_matrix",[[]])
		Dshape = Utils.getShapeOfMatrix(D)
		a = kwargs.get("attributes",  Dshape[1] )
        
		D1 = self.liu_scheme.encryptMatrix(
            plaintext_matrix = D,
            secret_key       = self.sk,
            m                = self.m
        )

		EU  = Utils.calculateUDM(plaintext_matrix = D)
		#EU = self.calculateUDM(D, a) #Calculo de la matriz UDM
		
		self.messageIntervals, self.cypherIntervals = self.fdh_ope.keyGen(D) #Generacion de los rangos de cada espacio
		sens = 0.01 #sensibilidad
		for x in range(len(EU)): #Cifrado de UDM 
			for y in range(x):
				for z in range(len(EU[x][y])):
					EU[x][y][z] = self.fdh_ope.encrypt(EU[x][y][z], sens, self.messageIntervals, self.cypherIntervals) #Función de cifrado de la matriz
		return D1, EU, self.messageIntervals, self.cypherIntervals


	

	"""
    description: dataowner participation for shift matrix decryption
    attributes:
        S1: shift matrix
        m: number of attributes of SK
    """
	def userActions(self, S1, m): #Participacion del data owner
		S = []
		for x in range(len(S1)): #Construccion de S
			S.append([])
		for i in range(len(S1)):
			for j in range(len(S1[i])):
				S[i].append(self.liu_scheme.decrypt(S1[i][j], self.sk, m)) #Descifrado con el esquema de Liu
		return S


	"""
    description: decrypt final clusters
    attributes:
        cipher_cluster: set of encrypted clusters
        m: number of attributes of SK
    """
	def verify(self, SK, m): 
		S = []
		for x in SK:
			S1 = []
			for y in x:
				S2 = []
				for z in y:
					S2.append(self.liu_scheme.decrypt(z, self.sk, m)) #Descifrado con el esquema de Liu
				S1.append(S2)
			S.append(S1)
		return S