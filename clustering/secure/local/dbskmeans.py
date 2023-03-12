import numpy as np
import copy
from time import time
from utils.Utils import Utils
from security.cryptosystem.liu import Liu
from security.cryptosystem.FDHOpe import Fdhope
from logger.Dumblogger import DumbLogger
from interfaces.clustering_result import ClusteringResult

"""
Description:
A  class to represent a double bind secure K-means algorithm
Attributes: 
	D1: Encrypted dataset 
	U: Updated distance matrix
	k: Number of clusters
	a: Number of attributes of D1
	m: Number of attributes of SK
	messageIntervals: Message space range
	cypherIntervals: Ciphertext space range
Variables:
	C: Set of clusters
"""
class Dbskmeans(object):

	def __init__(self,**kwargs):
		self.D1               = kwargs.get("ciphertext_matrix")
		self.U                = kwargs.get("UDM")
		self.k                = kwargs.get("k",2)
		D1Shape               = Utils.getShapeOfMatrix(self.D1)
		self.a                = kwargs.get("num_attributes",D1Shape[1])
		self.m                = kwargs.get("m",3)
		self.dataowner        = kwargs.get("dataowner") 
		self.messageIntervals = kwargs.get("messageIntervals") 
		self.cypherIntervals  = kwargs.get("cypherIntervals")
		self.sens             = kwargs.get("sens",0.01)
		self.max_iterations   = kwargs.get("max_iterations",100) #maximum number of possible iterations until it stops
		self.L                = kwargs.get("logger",DumbLogger()) #only for DEBUGGING purposes. 
		self.C                = list(map(lambda x:[self.D1[x].tolist()],list(range(0,self.k)))) #add the first k records of D to C
		self.Cent_i           = [self.D1[i] for i in range(self.k)] # initializes the set of centroids with the first record in D
		__C, label_vector     = Utils.populateClusters( #new set of C and label vector initial
            record_id         = self.k,
            UDM               = self.U,
            clusters          = self.C,
            ciphertext_matrix = self.D1,
		)
		#print("self.U",self.U.tolist())
		self.C      = __C
		self.Cent_j = Utils.calculateCentroids( #centroids are recalculated
			clusters   = self.C,
			k          = self.k,
			attributes = self.a,
			m          = self.m,
			Liu        = Liu
		)
		U, terminate = self.updateEncryptedUDM( #update matrix U and shift matrix
			UDM                 = self.U,
			previuous_centroids = self.Cent_i, 
			current_centroids   = self.Cent_j, 
		)
		self.label_vector = Utils.fillLabelVector( 
			label_vector  = label_vector,
			k             = self.k
		)
		self.terminate = terminate
		self.U = U
		self.run()

	"""
	Description: It allows working with the second part of the skmeans algorithm.
	"""
	def run(self,**kwargs):
		self.iteration_counter = 0 #initialization of the iteration counter variable

		while not self.terminate: #stops when shift matrix (S) is 0
			self.L.debug("SKMEANS[{}]".format(self.iteration_counter)) #save iteration counter in log
			C_empty           = Utils.empty_cluster(k = self.k) #restart C to place the new clusters
			__C, label_vector = Utils.populateClusters( #new set of C and new labeled vector
                record_id         = 0,
				UDM               = self.U,
				clusters          = C_empty,
				ciphertext_matrix = self.D1,
				centroids         = self.Cent_j,
			)
			C      = __C
			self.C = C 
			Cent_i = copy.copy(self.Cent_j) #reassign the elements of cent_j to cent_i
			self.L.debug("SKMEANS[{}] CALCULATE_CENTROIDS".format(self.iteration_counter)) #save iteration counter in log
			self.Cent_j = Utils.calculateCentroids( #centroids are recalculated
				clusters   = self.C,
				k          = self.k,
				attributes = self.a,
				m          = self.m,
				Liu        = Liu
			)
			self.L.debug("SKMEANS[{}] UPDATE_UDM".format(self.iteration_counter)) #save iteration counter in log
			U, terminate = self.updateEncryptedUDM( #update U and shift matrix
				UDM                 = self.U,
				previuous_centroids = Cent_i, 
				current_centroids   = self.Cent_j, 
			)
			self.terminate = terminate
			self.U = U
			self.L.debug("SKMEANS[{}] VERIFY_ZERO={}".format(self.iteration_counter,terminate)) #save iteration counter and temp in log
			self.label_vector = label_vector
			self.iteration_counter += 1 #increase number of iterations
			if(self.iteration_counter >= self.max_iterations): #if the iterations reach the maximum it stops
				temp = True
		return ClusteringResult(
        	label_vector = self.label_vector
   		)
	
	
	"""
	description:  Update encrypted UDM matrix.
	attributes:
		EU: Encrypted updatable distance matrix
		Cent_i: previous set of centroids
		Cent_j: next set of centroids
		m: number of attributes of SK
	"""
	def updateEncryptedUDM(self, **kwargs): #Proceso de actualizacion de la matriz EU
		UDM    = kwargs.get("UDM")
		UShape = Utils.getShapeOfMatrix(UDM)
		Cent_i = kwargs.get("previuous_centroids")
		Cent_j = kwargs.get("current_centroids")
		S1     = np.zeros((self.k,self.a,self.m)).tolist() #Fill S with 0

		for i in range(len(Cent_i)):
			for j in range(len(Cent_i[i])):
				S1[i][j] = Liu.subtract(ciphertext_1 = Cent_i[i][j], ciphertext_2 = Cent_j[i][j]) #subtract with Liu's scheme
		S = self.dataowner.userActions( #decryption by data owner #S -> 2D matrix
			shift_matrix = S1,
			m            = self.m
		)
		for x in range(len(S)): 
			for y in range(len(S[0])):
				S1[x][y] = Fdhope.encrypt( #Encrypt each element of S1 with the FDHOPE scheme
					plaintext    = S[x][y], 
					sens         = self.sens, 
					messagespace = self.messageIntervals, 
					cipherspace  = self.cypherIntervals
				)
		EUDM = []
		for x in range(UShape[0]): # construction of U1
			EUDM.append([]) #first dimension of U
			for y in range(self.k):
				EUDM[x].append([]) #second dimension of U
				for z in range(self.a):
					EUDM[x][y].append([]) #third dimension of U
					if y > x: #complete U is reviewed.
						EUDM[x][y][z] = ((-UDM[y][x][z] + S1[y][z])) #sum of each element of U with S
					else:
						EUDM[x][y][z] = (UDM[x][y][z] + S1[y][z]) #sum of each element of U with S
		terminate = Utils.verifyZero(S) #Check that matrix is 0
		return np.array(EUDM), terminate