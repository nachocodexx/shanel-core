import numpy as np
import copy
from utils.Utils import Utils
from security.cryptosystem.liu import Liu

class DumbLogger(object):
	def debug(self,x):
		return
	
	def info(self,x):
		return
	
	def error(self,x):
		return


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
class SKMeans(object):

	def __init__(self,**kwargs):
		self.D1             = kwargs.get("ciphertext_matrix")
		self.U              = kwargs.get("UDM")
		self.k              = kwargs.get("k",2)
		D1Shape             = Utils.getShapeOfMatrix(self.D1)
		self.a              = kwargs.get("num_attributes",D1Shape[1])
		self.m              = kwargs.get("m",3)
		self.dataowner      = kwargs.get("dataowner")
		self.max_iterations = kwargs.get("max_iterations",100)
		# Only for DEBUGGING purposes. 
		self.L              = kwargs.get("logger",DumbLogger())
		
		C_empty = Utils.empty_cluster(k = self.k)
		
		# Conjunto de los primeros k registros en D
		self.C       = Utils.appends(
			source  = self.D1, 
			dest    = C_empty, 
			dest_fx = Utils.dest_fx_matrix,
			limit   = self.k 
		)
		# 
		
		self.Cent_i  = Utils.appends(
			source  = self.D1,
			dest    = [],
			dest_fx = Utils.dest_fx_vector,
			limit   = self.k
		) 
		# _________________________________________ 
		
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

		U, S = self.updateUDM(
			UDM = self.U,
			previuous_centroids=self.Cent_i, 
			current_centroids=self.Cent_j, 
		)
		
		self.label_vector = Utils.fillLabelVector(
			label_vector = label_vector,
			k            = self.k
		)

		self.S = S
		self.U = U
		# ________________________________________
		self.run(
		 	ciphertext_matrix = self.D1,
		 	UDM = self.U,
		 	previuous_centroids = self.Cent_j
		)

	def run(self,**kwargs):
		temp   = Utils.verifyZero(self.S)
		self.iteration_counter = 0
		#self.label_vector = []
		# pbar = tqdm(total=self.max_iterations)
		while not temp: #Se detiene cuando la matriz de desplazamiento S es 0
			self.L.debug("SKMEANS[{}]".format(self.iteration_counter))
			C_empty = Utils.empty_cluster(k = self.k)

			__C, label_vector = Utils.populateClusters(
                record_id = 0,
				UDM       = self.U,
				clusters  = C_empty,
				ciphertext_matrix = self.D1,
				centroids = self.Cent_j,
			)
			C = __C
			self.C = C 
			Cent_i = copy.copy(self.Cent_j) #Reasigna los elementos de cent_j a cent_i
			
			self.L.debug("SKMEANS[{}] CALCULATE_CENTROIDS".format(self.iteration_counter))
			self.Cent_j = Utils.calculateCentroids(
				clusters   = self.C,
				k          = self.k,
				attributes = self.a,
				m          = self.m,
				Liu        = Liu
			)
			self.L.debug("SKMEANS[{}] UPDATE_UDM".format(self.iteration_counter))
			U, S = self.updateUDM(
				UDM = self.U,
				previuous_centroids=Cent_i, 
				current_centroids=self.Cent_j, 
			)
			self.U = U
			temp = Utils.verifyZero(S)
			self.L.debug("SKMEANS[{}] VERIFY_ZERO={}".format(self.iteration_counter,temp))
			self.label_vector = label_vector
			self.iteration_counter += 1
			if(self.iteration_counter >= self.max_iterations):
				temp = True
			# pbar.update(1)
			# progress += 1
			# print("ITERATION[{}]".format(self.iteration_counter))
			# print("")
		return self.C,self.label_vector
	
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
	def updateUDM(self, **kwargs): #Proceso de actualizacion de la matriz U
		U      = kwargs.get("UDM")
		Cent_i = kwargs.get("previuous_centroids")
		Cent_j = kwargs.get("current_centroids")
		# ________________________________________________________ 
		S1     = np.zeros((self.k,self.a,self.m)).tolist()
		for i in range(len(Cent_i)):
			for j in range(len(Cent_i[i])):
				S1[i][j] = Liu.subtract(ciphertext_1 = Cent_i[i][j], ciphertext_2 = Cent_j[i][j]) #Resta con el esquema de Liu	
		# ______________________________________________________________________________
		#print(S1)
		#time.sleep(5)
		S = self.dataowner.userActions(
			shift_matrix = S1,
			m            = self.m
		) #Descifrado por parte del data owner #S -> matriz 2D  

		U1 = []
		# np.zeros((len(U),len(S),len(S[0])))
		for x in range(len(U)): ##Construcción de U1 vacia
			U1.append([])
			for y in range(self.k):
				U1[x].append([])
				for z in range(self.a):
					U1[x][y].append([])
					if y > x: #Se revisa U completa.
						U1[x][y][z] = ((-U[y][x][z] + S[y][z])) #Suma de cada elemento de U con S
					else:
						U1[x][y][z] = (U[x][y][z] + S[y][z]) #Suma de cada elemento de U con S

		return U1,S #Triangulo inferior de U y matriz de desplazamiento