import numpy as np
import copy
from utils.Utils import Utils
from security.cryptosystem.liu import Liu
from security.cryptosystem.FDHOpe import FDHOpe

"""
Description:
A  class to represent a secure K-means algorithm
_______________
Attributes: 
	D1: Encrypted dataset 
	U: Updated distance matrix
	k: Number of clusters
	a: Number of attributes of D1
	m: number of attributes of SK
Variables:
	C: Set of clusters
"""
class DBSKMeans(object):

	def __init__(self,**kwargs):
		self.D1               = kwargs.get("ciphertext_matrix")
		self.U                = kwargs.get("UDM")
		self.k                = kwargs.get("k",2)
		self.D1Shape          = Utils.getShapeOfMatrix(self.D1)
		self.a                = kwargs.get("num_attributes",self.D1Shape[1])
		self.m                = kwargs.get("m",3)
		self.dataowner        = kwargs.get("dataowner")
		self.messageIntervals = kwargs.get("messageIntervals")
		self.cypherIntervals  = kwargs.get("cypherIntervals")
		self.sens             = kwargs.get("sens",0.01)
		self.max_iterations   = kwargs.get("max_iterations",100)
		
		C_empty        = Utils.empty_cluster(k = self.k)

		self.C       = Utils.appends(
			source  = self.D1, 
			dest    = C_empty, 
			dest_fx = Utils.dest_fx_matrix,
			limit   = self.k 
		) # Conjunto de los primeros k registros en D
		
		self.Cent_i  = Utils.appends(
			source  = self.D1,
			dest    = [],
			dest_fx = Utils.dest_fx_vector,
			limit   = self.k
		) 

		__C, label_vector = Utils.populateClusters(
            record_id = self.k,
            UDM       = self.U,
            clusters  = self.C,
            ciphertext_matrix = self.D1,
		)
		self.C = __C
		
		self.Cent_j = Utils.calculateCentroids(
			clusters   = self.C,
			k          = self.k,
			attributes = self.a,
			m          = self.m,
			Liu        = Liu
		)
		
		U, terminate = self.updateEncryptedUDM(
			UDM = self.U,
			previuous_centroids=self.Cent_i, 
			current_centroids=self.Cent_j, 
		)
		
		self.U = U

		self.run(
		 	ciphertext_matrix = self.D1,
		 	UDM = self.U,
		 	previuous_centroids = self.Cent_j,
			terminate = terminate
		)

	"""
	"""
	def run(self,**kwargs):
		self.iteration_counter = 0
		self.label_vector      = []
		self.terminate         = kwargs.get("terminate",False)
		
		while not self.terminate: #while terminate is False
			C_empty = Utils.empty_cluster(k = self.k)

			C, label_vector = Utils.populateClusters(
                record_id = 0,
				UDM       = self.U,
				clusters  = C_empty,
				ciphertext_matrix = self.D1,
				centroids = self.Cent_j,
			)
			self.C = C 
			Cent_i = copy.copy(self.Cent_j) #Reasigna los elementos de cent_j a cent_i
			
			

			self.Cent_j = Utils.calculateCentroids(
				clusters   = self.C,
				k          = self.k,
				attributes = self.a,
				m          = self.m,
				Liu        = Liu
			)

			#print(self.Cent_j)
			#print("_"*100)

			U, terminate = self.updateEncryptedUDM(
				UDM                 = self.U,
				previuous_centroids = Cent_i, 
				current_centroids   = self.Cent_j, 
			)

			self.terminate          = terminate
			self.U                  = U
			self.label_vector       = label_vector
			self.iteration_counter += 1
			if(self.iteration_counter >= self.max_iterations) :
				self.terminate = True
			
		return self.C, self.label_vector
	
	
	"""
	description:  Update encrypted UDM matrix.
	attributes:
		EU: Encrypted updatable distance matrix
		Cent_i: previous set of centroids
		Cent_j: next set of centroids
		m: number of attributes of SK
	"""
	def updateEncryptedUDM(self, **kwargs): #Proceso de actualizacion de la matriz EU
		U      = kwargs.get("UDM")
		Cent_i = kwargs.get("previuous_centroids")
		Cent_j = kwargs.get("current_centroids")
		S1     = np.zeros((self.k,self.a,self.m)).tolist()
		
		for i in range(len(Cent_i)):
			for j in range(len(Cent_i[i])):
				S1[i][j] = Liu.subtract(Cent_i[i][j], Cent_j[i][j]) #Resta con el esquema de Liu	
				

		S = self.dataowner.userActions(
			shift_matrix = S1,
			m            = self.m
		) #Descifrado por parte del data owner #S -> matriz 2D 
		
		for x in range(len(S)):
			for y in range(len(S[x])):
				S1[x][y] = FDHOpe.encrypt(
					v                = S[x][y], 
					sens             = self.sens, 
					messageIntervals = self.messageIntervals, 
					cypherIntervals  = self.cypherIntervals
				) #Cifrado de S
		#print(S1)

		EU1 = []
		# for x in range(len(U)): ##Construcción de U1 vacia
		for x in range(len(U)): ##Construcción de U1 vacia
			EU1.append([])
			for y in range(self.k):
				EU1[x].append([])
				for z in range(self.a):
					EU1[x][y].append([])
					if y > x: #Se revisa U completa.
						EU1[x][y][z] = ((-U[y][x][z] + S[y][z])) #Suma de cada elemento de U con S
					else:
						EU1[x][y][z] = (U[x][y][z] + S[y][z]) #Suma de cada elemento de U con S
		# ________________________________________________________________
		# temp = True
		# for t in S:
		# 	t = [0 if element==0.0 else element for element in t] #Reemplazar 0.0 por 0
		# 	temp2 = True
		# 	for u in t:
		# 		if u != 0:
		# 			temp2 = False
		# 	if not temp2:
		# 		temp = False
		# _______________________________________________________________
		# if temp: #Se detiene cuando la matriz de desplazamiento S es 0
		# 	terminate = True
		# else:
		# 	terminate = False
		terminate = Utils.verifyZero(S)
		return EU1, terminate #Triangulo inferior de U y matriz de desplazamiento            