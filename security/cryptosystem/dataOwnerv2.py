import math
from liu import Liu

class DataOwner:


	def outsourcedData(self, rawD, a, m): #Preparacion de los datos #Raw = dataset original, a = numero de atributos, m 
		#print(rawD)
		liu_scheme = Liu()
		sk = liu_scheme.secretKey(m)
		D = rawD
		#print(D)
		D1, U = [], [] 
		for r in D: ##Cifrado de cada elemento de D
			D2 = [] 
			for v in r:
				D2.append(liu_scheme.encrypt(v, sk)) #Funcion cifrado con el esquema de Liu
			D1.append(D2)
		#D1 = [[[0.59, 0.70, 1.59], [0.71, 2.21, 1.13]], [[0.54, 0.42, 1.36], [0.58, 1.07, 1.19]], [[0.40, 1.45, 0.32], [0.54, 0.76, 1.13]], [[0.34, 1.15, 0.56], [0.65, 1.76, 1.13]], [[0.83, 1.35, 1.68], [0.46, 1.07, 0.86]], [[0.64, 1.27, 1.27], [0.35, 0.66, 0.55]], [[0.22, 0.27, 0.57], [0.47, 0.40, 1.16]], [[0.42, 0.93, 0.87], [0.66, 1.89, 1.05]]]
		#D1 = [[[0.073, 0.365, 0.167], [0.602, 0.160, 1.580], [0.696, 0.461, 1.960], [0.176, 0.277, 0.423], [0.635, 0.129, 1.661], [0.234, 0.377, 0.626], [0.321, 0.250, 0.823], [0.170, 0.350, 0.435], [0.314, 0.220, 0.791], [0.111, 0.174, 0.200]], [[0.050, 0.378, 0.107], [0.298, 0.073, 0.690], [0.051, 0.483, 0.150], [0.150, 0.485, 0.430], [0.661, 0.432, 1.850], [0.609, 0.465, 1.716], [0.118, 0.325, 0.279], [0.614, 0.376, 1.696], [0.601, 0.180, 1.585], [0.367, 0.278, 0.961]], [[0.183, 0.465, 0.335], [0.197, 0.513, 0.393], [0.176, 0.531, 0.339], [0.171, 0.530, 0.325], [0.086, 0.351, 0.018], [0.669, 0.484, 1.712], [0.330, 0.230, 0.659], [0.112, 0.601, 0.187], [0.343, 0.456, 0.782], [0.265, 0.345, 0.520]], [[0.249, 0.599, 0.572], [0.713, 0.418, 1.811], [0.534, 0.281, 1.255], [0.227, 0.408, 0.437], [0.252, 0.309, 0.469], [0.093, 0.497, 0.092], [0.521, 0.364, 1.250], [0.256, 0.208, 0.444], [0.629, 0.608, 1.647], [0.169, 0.586, 0.341]], [[0.124, 0.560, 0.024], [0.696, 0.541, 1.630], [0.719, 0.667, 1.742], [0.102, 0.693, 0.015], [0.329, 0.707, 0.658], [0.772, 0.706, 1.907], [0.299, 0.746, 0.589], [0.765, 0.820, 1.932], [0.342, 0.746, 0.711], [0.731, 0.703, 1.791]], [[0.350, 0.676, 0.706], [0.660, 0.751, 1.610], [0.513, 0.724, 1.184], [0.620, 0.458, 1.386], [0.552, 0.944, 1.380], [0.530, 0.686, 1.218], [0.294, 0.733, 0.570], [0.120, 0.626, 0.039], [0.163, 0.739, 0.204], [0.178, 0.837, 0.284]]]
		#print(self.sk)


		for x in range(len(D)): #Llenado de U con distancias entre los datos en plano
			newRowX = []
			for y in range(x+1):
				newDistanceVect = []
				for z in range(a):
					Uxyz = (D[x][z] - D[y][z]) #Calculo de distancias
					newDistanceVect.append(Uxyz)
				newRowX.append(newDistanceVect)
			U.append(newRowX)

		return D1,U,sk


	def userActions(self, S1, sk): #Participacion del data owner
		liu_scheme = Liu()
		S = []
		for r in S1: #Descifrado de cada elemento de S1
			S2 = []
			for v in r:
				S2.append(liu_scheme.decrypt(v, sk)) #Descifrado con el esquema de Liu
			S.append(S2)
		return S


	def decryptClusters(self, C, sk): #
		liu_scheme = Liu()
		Clusters = []
		for clust in C: #Descifrado de cada elemento de S1
			clustPlain = []
			for rec in clust:
				S2 = []
				for val in rec:
					S2.append(liu_scheme.decrypt(val, sk)) #Descifrado con el esquema de Liu
				clustPlain.append(S2)
			Clusters.append(clustPlain)
		return Clusters

	def test(self):
		D = [[0.73,8.84],[49.93,34.44],[0.57,65.04],[62.15,32.29],[59.47,36.04]]
		m = 3

		dataowner = DataOwner()
		D1,U, sk = dataowner.outsourcedData(D,2,m)

		print("Encrypted data: ")
		for ren in D1:
			print(ren)

		print("U: ")
		for ren in U:
			print(ren)

		Drec = dataowner.userActions(D1, sk)  #descifrado

		print("D: ")
		for ren in Drec:
			print(ren)
		return

#dataowner = DataOwner()
#dataowner.test()