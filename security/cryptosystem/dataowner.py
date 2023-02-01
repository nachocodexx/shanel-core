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
	liu_scheme: Liu <object>
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

	"""
	description: Data preparation.
	attributes: 
		plaintext_matrix: original dataset (numerical)
		a: number of attributes of D
		threshold: how close the records must be to belong to the same cluster
		algorithm: clustering algorithm to use
	"""
	def outsourcedData(self,**kwargs):
		plaintext_matrix = kwargs.get("plaintext_matrix",[[]])
		Dshape           = Utils.getShapeOfMatrix(plaintext_matrix)
		a                = kwargs.get("attributes",  Dshape[1] )
		threshold        = kwargs.get("threshold",0.01)
		algorithm        = kwargs.get("algorithm","SKMEANS")

		encryption_result = self.liu_scheme.encryptMatrix( #The plaintext is sent to Liu scheme to encrypt
			plaintext_matrix = plaintext_matrix,
			secret_key       = self.sk,
			m                = self.m
		)

		start_time_udm = time() 
		U, encrypted_threshold = self.get_U( #U is generated according to the chosen algorithm
			algorithm         = algorithm,
			plaintext_matrix  = plaintext_matrix,
			threshold         = threshold
		)
		udm_time = time() - start_time_udm

		return OutsourceDataStats(
			UDM                   = U,
			udm_time              = udm_time, 
			encrypted_matrix      = encryption_result.matrix,
			encrypted_matrix_time = encryption_result.encryption_time,
			messageIntervals      = self.messageIntervals,
			cypherIntervals       = self.cypherIntervals,
			encrypted_threshold   = encrypted_threshold
		)

	"""
	description: allows to generate the matrix U according to the type of algorithm to use
	attributes:
		plaintext_matrix: original dataset (numerical)
		threshold: how close the records must be to belong to the same cluster
		algorithm: clustering algorithm to use
	"""
	def get_U(self,**kwargs):
		plaintext_matrix = kwargs.get("plaintext_matrix")
		threshold        = kwargs.get("threshold")
		algorithm        = kwargs.get("algorithm")
		encrypted_threshold = 0 #threshold is 0 if not required by the algorithm

		if (algorithm == "SKMEANS"): 
			U  = Utils.create_UDM( #Matrix UDM is created
				plaintext_matrix = plaintext_matrix
				)

		elif(algorithm == "DBSKMEANS"):
			EU  = Utils.create_UDM( # Matrix UDM is created
				plaintext_matrix = plaintext_matrix
				)
			self.messageIntervals, self.cypherIntervals = Fdhope.keygen( #the intervals (SK) of each space are generated
			dataset = EU
			)
			U = self.encrypt_U( #Matrix EU is encrypted
				U = EU,
				algorithm = algorithm
			)

		elif(algorithm == "DBSNNC"):
			ED  = Utils.calculateDM( #Matrix ED is created
				plaintext_matrix = plaintext_matrix
			)
			self.messageIntervals, self.cypherIntervals = Fdhope.keygen( #the intervals (SK) of each space are generated
			dataset = ED
			)
			U = self.encrypt_U( #Matrix EU is encrypted
				U = ED,
				algorithm = algorithm
			)
			encrypted_threshold = Fdhope.encrypt( #Threshold is encrypted
				plaintext    = threshold,
				messagespace = self.messageIntervals, 
				cipherspace  = self.cypherIntervals
			)

		return U, encrypted_threshold


	"""
	description: allows to encrypt the U
	attributes:
		U: matrix to be encrypted
		algorithm: clustering algorithm to use
	"""
	def encrypt_U(self,**kwargs):
		U                = kwargs.get("U")
		algorithm        = kwargs.get("algorithm")

		for x in range(len(U)): 
			for y in range(x):
				
				if (algorithm == "DBSKMEANS"): #if the algorithm is dbskmeans, one more dimension needs to be traversed
					for z in range(len(U[x][y])):
						U[x][y][z] = Fdhope.encrypt( #the lower triangle of U is encrypted
							plaintext    = U[x][y][z], 
							sens         = self.sens, 
							messagespace = self.messageIntervals, 
							cipherspace  = self.cypherIntervals
						)
						U[y][x][z] = U[x][y][z] #the equivalent position is obtained to fill the upper triangle
				
				elif(algorithm == "DBSNNC"):
					U[x][y] = Fdhope.encrypt( #the lower triangle of U is encrypted
						plaintext    = U[x][y], 
						messagespace = self.messageIntervals, 
						cipherspace  = self.cypherIntervals
					)
					U[y][x] = U[x][y] #the equivalent position is obtained to fill the upper triangle
		return U


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