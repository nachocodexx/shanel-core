import numpy as np
import copy
from utils.Utils import Utils
from security.cryptosystem.liu import Liu
from logger.Dumblogger import DumbLogger
from interfaces.clustering_result import ClusteringResult

"""
Description:
A  class to represent a secure K-means algorithm
Attributes: 
	D1: Encrypted dataset 
	U: Updated distance matrix
	k: Number of clusters
	a: Number of attributes of D1
	m: number of attributes of SK
Variables:
	C: Set of clusters
"""
class SKMeans(object):

	def __init__(self,**kwargs):
		self.D1             = kwargs.get("ciphertext_matrix")
		self.U              = kwargs.get("UDM")
		self.k              = kwargs.get("k",2)
		D1Shape             = Utils.getShapeOfMatrix(self.D1)
		self.a              = kwargs.get("num_attributes",D1Shape[1])
		self.m              = kwargs.get("m",3)
		self.dataowner      = kwargs.get("dataowner") 
		self.max_iterations = kwargs.get("max_iterations",100) #maximum number of possible iterations until it stops
		self.L              = kwargs.get("logger",DumbLogger()) #only for DEBUGGING purposes. 
		self.C              = list(map(lambda x:[self.D1[x].tolist()],list(range(0,self.k)))) #add the first k records of D to C
		self.Cent_i         = [self.D1[i] for i in range(self.k)] # initializes the set of centroids with the first record in D
		__C, label_vector   = Utils.populateClusters( #new set of C and label vector initial
            record_id         = self.k,
            UDM               = self.U,
            clusters          = self.C,
            ciphertext_matrix = self.D1,
		)
		self.C      = __C
		self.Cent_j = Utils.calculateCentroids( #centroids are recalculated
			clusters   = self.C,
			k          = self.k,
			attributes = self.a,
			m          = self.m,
			Liu        = Liu
		)
		U, S = self.updateUDM( #update matrix U and shift matrix
			UDM                 = self.U,
			previuous_centroids = self.Cent_i, 
			current_centroids   = self.Cent_j, 
		)
		self.label_vector = Utils.fillLabelVector( 
			label_vector  = label_vector,
			k             = self.k
		)
		self.S = S
		self.U = U
		self.run()

	"""
	Description: It allows working with the second part of the skmeans algorithm.
	"""
	def run(self,**kwargs):
		temp                   = Utils.verifyZero(self.S) #boolean variable that checks if Shift matrix had changes
		self.iteration_counter = 0 #initialization of the iteration counter variable

		while not temp: #stops when shift matrix (S) is 0
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
			U, S = self.updateUDM( #update U and shift matrix
				UDM                 = self.U,
				previuous_centroids = Cent_i, 
				current_centroids   = self.Cent_j, 
			)
			self.U = U
			temp   = Utils.verifyZero(S) #boolean variable that checks if Shift matrix had changes
			self.L.debug("SKMEANS[{}] VERIFY_ZERO={}".format(self.iteration_counter,temp)) #save iteration counter and temp in log
			self.label_vector = label_vector
			self.iteration_counter += 1 #increase number of iterations
			if(self.iteration_counter >= self.max_iterations): #if the iterations reach the maximum it stops
				temp = True
		return ClusteringResult(
        	label_vector = self.label_vector
   		)
	
	"""
	description:  Update UDM matrix.
		A UDM matrix is a 3D matrix containing distances between the attribute values in each record
		and the corresponding attribute values in all other records.
	attributes:
		U: Updatable distance matrix
		Cent_i: previous set of centroids
		Cent_j: next set of centroids
		m: number of attributes of SK
	"""
	def updateUDM(self, **kwargs): #U matrix update process
		U      = kwargs.get("UDM")
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
		U1 = []
		for x in range(len(U)): # construction of U1
			U1.append([]) #first dimension of U
			for y in range(self.k):
				U1[x].append([]) #second dimension of U
				for z in range(self.a):
					U1[x][y].append([]) #third dimension of U
					if y > x: #complete U is reviewed.
						U1[x][y][z] = ((-U[y][x][z] + S[y][z])) #sum of each element of U with S
					else:
						U1[x][y][z] = (U[x][y][z] + S[y][z]) #sum of each element of U with S
		return U1,S

if __name__ == "__main__":
	D = np.load("D:/scs/testing/SKMEANS_matrix.npy")
	UDM = np.load("D:/scs/testing/SKMEANS_udm.npy")