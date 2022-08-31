import copy
import time
from liu import Liu
from dataOwner import DataOwner

class Tpdm:

	def sK_Means(self, D1, U, k, dataowner,sk):
		a = len(D1[0])
		C = [] #Conjunto de k clusters vacios. Cada cluster es un vector de registros de D'
		for x in range(k):
			C.append([])

		#ahora cada cluster se le asigna los k primeros registros de D', uno por cluster
		for x in range(k):
			C[x].append(copy.deepcopy(D1[x]))

		#centroides, los primeros k registros en D'
		CentAct = []
		for x in range(k): #Llenado de Cent_i con los primeros k registros de D1
			CentAct.append(copy.deepcopy(D1[x]))

		iters = 0

		print("\nSK-means #ITER = ", iters)
		self.printClusters(C)
		self.printCentroids(CentAct)

		#va el primer calculo de clusters con U inicial: todos los registros de D1 contra los primeros k
		iters += 1

		C = self.populateClusters(k, U, C, D1, CentAct)
		# con los nuevos clusters, calcula los nuevos centroides
		CentSig = self.calculateCentroids(C, k, a)

		print("\nSK-means #ITER = ", iters)
		self.printClusters(C)
		self.printCentroids(CentSig)

		#con los centroides primero y segundo actualiza la la tabla U y verifica si hubo convegencia (S = 0)
		S,U = self.updateUDM(U, CentAct, CentSig,dataowner,sk)
		temp = self.verifyZero(S)  # Verifica que la matriz de desplazamiento sea 0

		while temp is False:

			iters += 1

			C = []  # Conjunto de k clusters vacios. Cada cluster es un vector de registros de D'
			for x in range(k):
				C.append([])

			C = self.populateClusters(0, U, C, D1, CentSig)

			CentAct = copy.deepcopy(CentSig)

			CentSig = []

			CentSig = self.calculateCentroids(C, k, a)

			print("\nSK-means #ITER = ", iters)
			self.printClusters(C)
			self.printCentroids(CentAct)

			S, U = self.updateUDM(U, CentAct, CentSig, dataowner, sk)

			temp = self.verifyZero(S)

		return C,iters

	def populateClusters(self, rid, U, C, D1, Cent_i):  # Determina la similitud entre los centroides y los registros en D1
		# print(U)
		id = -1
		for x in range(rid,len(D1)): #cada registro x
			menor = 1000000
			for y in range(len(Cent_i)):  # desde 0 hasta k
				sim = 0  # calculala similaridad del registro x en D' con el centroide y en Cent_i
				record = []
				if (y > x):
					record = U[y][x]
				else:
					record = U[x][y]
				for val in record:  # desde 0 hasta el total de atributos
					sim = sim + abs(val)

				if (sim < menor):
					menor = sim
					id = y
			C[id].append(copy.deepcopy(D1[x]))
		return C

	def calculateCentroids(self, C, k, a): #Nuevo conjunto de centroides
		liu_scheme = Liu()   #se usarán las prop homomorficas

		Centp = []  #k-elements empty set

		for j in range(k):  #procesa el cluster j
			#average tiene a elementos, cada uno de m componentes
			#inicialmente, es el primer registro del cluster
			Regs = copy.deepcopy(C[j])
			Average = copy.deepcopy(Regs[0])
			for i in range(1,len(Regs)):
				Rec = Regs[i]
				for q in range(a):
					Average[q] = liu_scheme.add(Average[q],Rec[q])

			for q in range(a):
				Average[q] = liu_scheme.multiply_c(1/len(Regs),Average[q])

			Centp.append(copy.deepcopy(Average))

		return Centp

	def updateUDM(self, U, Cent_i, Cent_j,dataowner,sk):  # Proceso de actualizacion de la matriz U
		S1 = [] #tendra k elementos
		liu_scheme = Liu()  # se usarán las prop homomorficas

		for k in range(len(Cent_i)):
			centi = Cent_i[k]
			centj = Cent_j[k]
			rowS = []
			for q in range(len(centi)):
				newCent_q = liu_scheme.subtract(centi[q],centj[q])
				rowS.append(copy.deepcopy(newCent_q))
			S1.append(copy.deepcopy(rowS))

		print("\n\tS': ", len(S1), " rows")
		for row in S1:
			print("\t", row)

		# decifra S'

		S = dataowner.userActions(S1, sk)
		print("\tSdecrypted: ", len(S), " rows")
		for row in S:
			print("\t", row)

		#actualiza U,
		#cada renglon de S, de long a, es visto como un registro y, del que se mide la distancia a cada registro x

		kval = len(S)
		aval = len(S[0])
		for y in range(kval):  #todos los registros x se compararán con cada registro y en S
			for x in range(y,len(U)):
				for z in range(aval):
					U[x][y][z] = U[x][y][z] + S[y][z]

		print("\tNew U: ", len(U), " rows")
		for row in U:
			print("\t",len(row), ": ", row)

		return S,U

	def verifyZero(self, S): #S is a set o k rows, each with a elements
		for t in S: #each row
			for e in t:
				if (e != 0):
					return False
		return True

	def printClusters(self, C):
		print("\tClusters:")
		for i in range(len(C)):
			print("\tclst-",i,"(",len(C[i]), "elements): ", C[i])
		return

	def printCentroids(self, Cent):
		print("\tCentroids:")
		for i in range(len(Cent)):
			print("\tcent-", i,": ", Cent[i])
		return

D = [[0.73,8.84],[49.93,34.44],[0.57,65.04],[62.15,32.29],[59.47,36.04]]
m = 3


#D = [[2,10], [5,8], [1,2], [2,5], [8,4], [7,5],[6,4],[4,9]]
print("Data: ")
for ren in D:
	print(ren)

dataowner = DataOwner()
D1,U,sk = dataowner.outsourcedData(D,2,m)

print("Encrypted data: ")
for ren in D1:
	print(ren)

print("U: ")
for ren in U:
	print(ren)

tpdm = Tpdm()

k = 2

clusters,iter = tpdm.sK_Means(D1,U,k,dataowner,sk)
decrypted = dataowner.decryptClusters(clusters, sk)

print("\nFinal CLUSTERS (", iter," iterations )")
tpdm.printClusters(decrypted)