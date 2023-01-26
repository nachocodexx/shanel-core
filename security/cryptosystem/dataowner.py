import numpy as np
from utils.Utils import Utils
from .FDHOpe import Fdhope
from time import time


class OutsourceDataStats(object):
	def __init__(self,**kwargs):
		self.udm_time              = kwargs.get("udm_time",0)
		self.UDM                   = kwargs.get("UDM",np.array([]))
		self.encrypted_matrix      = kwargs.get("encrypted_matrix",np.array([]))
		self.encrypted_matrix_time = kwargs.get("encrypted_matrix_time",np.array([]))
		self.messageIntervals      = kwargs.get("messageIntervals",{})
		self.cypherIntervals       = kwargs.get("cypherIntervals",{})
		self.encrypted_threshold   = kwargs.get("encrypted_threshold",0)
	

"""
Description:
	A class that represents the preparation step, performed by data owners, 
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
class DataOwner(object):

	def __init__(self,**kwargs):
		m               = kwargs.get("m")
		liu_scheme      = kwargs.get("liu_scheme")
		self.sens       = kwargs.get("sens",0.01)
		self.m          = m 
		self.liu_scheme = liu_scheme
		self.sk         = self.liu_scheme.secretKey( m = self.m )
		self.messageIntervals, self.cypherIntervals = {}, {}

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
		# encryption_result: ciphertext_matrix, U: UDM  
		encryption_result = self.liu_scheme.encryptMatrix(
			plaintext_matrix = D,
			secret_key       = self.sk,
			m                = self.m
		)
		U  = Utils.create_UDM(plaintext_matrix = D)
		return encryption_result,U

	"""
	description: Data preparation.
	attributes: 
		rawD: original dataset
		D: numeric dataset
		a: number of attributes of D
		m: number of attributes of SK
	"""
	def outsourcedDataAndStats(self,**kwargs):
		# ____________
		#   Transform: rawD -> D(numeric) 
		# ___________
		D      = kwargs.get("plaintext_matrix",[[]])
		Dshape = Utils.getShapeOfMatrix(D)
		a = kwargs.get("attributes",  Dshape[1] )
		encryption_result = self.liu_scheme.encryptMatrix(
			plaintext_matrix = D,
			secret_key       = self.sk,
			m                = self.m
		)
		
		start_time_udm = time()
		U  = Utils.create_UDM(plaintext_matrix = D)
		udm_time = time()  - start_time_udm
		return OutsourceDataStats(
			UDM = U,
			udm_time = udm_time, 
			encrypted_matrix = encryption_result.matrix,
			encrypted_matrix_time = encryption_result.encryption_time
		)

	"""
	description: Data preparation.
	attributes: 
		rawD: original dataset
		D: numeric dataset
		a: number of attributes of D
		m: number of attributes of SK
	"""
	def outsourcedDataVectorizeAndStats(self,**kwargs):
		# ____________
		#   Transform: rawD -> D(numeric) 
		# ___________
		D                 = kwargs.get("plaintext_matrix",[[]])
		Dshape            = Utils.getShapeOfMatrix(D)
		N                 = Dshape[0]
		a                 = kwargs.get("attributes",  Dshape[1] )
		# 
		udm_init          = kwargs.get("udm_init","zeros")
		encryption_result = self.liu_scheme.encryptMatrix(
			plaintext_matrix = D,
			secret_key       = self.sk,
			m                = self.m
		)

		start_time_udm    = time()
		U                 = np.zeros((N,N,a)).tolist() if(udm_init == "zeros" )  else Utils.create_UDM(plaintext_matrix = D)
		udm_time          = time()  - start_time_udm
		# ________________________________________________________________________________________________________________
		return OutsourceDataStats(
			UDM = U,
			udm_time = udm_time, 
			encrypted_matrix = encryption_result.matrix,
			encrypted_matrix_time = encryption_result.encryption_time
		)


	"""
	description: Data preparation.
	attributes: 
		rawD: original dataset
		D: numeric dataset
		a: number of attributes of D
		m: number of attributes of SK
	"""
	def outsourceDataDBS(self, **kwargs): 
		D      = kwargs.get("plaintext_matrix",[[]])
		Dshape = Utils.getShapeOfMatrix(D)
		a      = kwargs.get("attributes",  Dshape[1] )
		#algorithm = kwargs.get("algorithm", 1)

		encryption_result = self.liu_scheme.encryptMatrix(
			plaintext_matrix = D,
			secret_key       = self.sk,
			m                = self.m
		)

		EU  = Utils.calculateUDM(plaintext_matrix = D)

		self.messageIntervals, self.cypherIntervals = Fdhope.keygen( #Generacion de los rangos de cada espacio
			dataset = EU
			)
		start_time_udm    = time()
		for x in range(len(EU)): #Cifrado de UDM 
			for y in range(x):
				for z in range(len(EU[x][y])):
					EU[x][y][z] = Fdhope.encrypt(
						plaintext    = EU[x][y][z], 
						sens         = self.sens, 
						messagespace = self.messageIntervals, 
						cipherspace  = self.cypherIntervals
					) #Función de cifrado de la matriz
		udm_time          = time()  - start_time_udm
		
		return OutsourceDataStats(
			UDM                   = EU,
			udm_time              = udm_time, 
			encrypted_matrix      = encryption_result.matrix,
			encrypted_matrix_time = encryption_result.encryption_time,
			messageIntervals      = self.messageIntervals,
			cypherIntervals       = self.cypherIntervals
			)
		#return encryption_result, EU, self.messageIntervals, self.cypherIntervals

	"""
	description: Data preparation.
	attributes: 
		rawD: original dataset
		D: numeric dataset
		a: number of attributes of D
		m: number of attributes of SK
	"""
	def outsourceDataDbsnnc(self, **kwargs): 
		D         = kwargs.get("plaintext_matrix",[[]])
		Dshape    = Utils.getShapeOfMatrix(D)
		a         = kwargs.get("attributes",  Dshape[1] )
		threshold = kwargs.get("threshold",0.01)

		encryption_result = self.liu_scheme.encryptMatrix(
			plaintext_matrix = D,
			secret_key       = self.sk,
			m                = self.m
		)

		EU  = Utils.calculateDM(plaintext_matrix = D)
		
		self.messageIntervals, self.cypherIntervals = Fdhope.keygen( #Generacion de los rangos de cada espacio
			dataset   = EU
			)

		start_time_udm    = time()

		for x in range(len(EU)): #Cifrado de UDM 
			for y in range(x):
				EU[x][y] = Fdhope.encrypt(
					plaintext    = EU[x][y], 
					messagespace = self.messageIntervals, 
					cipherspace  = self.cypherIntervals
				)
				EU[y][x] = EU[x][y]
				 #Función de cifrado de la matriz
		udm_time          = time()  - start_time_udm 

		encrypted_threshold = Fdhope.encrypt(
			plaintext    = threshold,
			messagespace = self.messageIntervals, 
			cipherspace  = self.cypherIntervals
		)
		
		return OutsourceDataStats(
			UDM                   = EU,
			udm_time              = udm_time, 
			encrypted_matrix      = encryption_result.matrix,
			encrypted_matrix_time = encryption_result.encryption_time,
			messageIntervals      = self.messageIntervals,
			cypherIntervals       = self.cypherIntervals,
			encrypted_threshold   = encrypted_threshold
			)
		#return encryption_result, EU, self.messageIntervals, self.cypherIntervals


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
