import numpy as np
import pandas as pd
import requests
# from constants import Constants
# from core.security.cryptosystem.liu import Liu
from uuid import uuid4
# ___________________________________________________

class Utils(object):
    def __init__(self):

        pass

    def repeatRequestByHeaders(**kwargs):
        STATUS          = {"COMPLETED":0,"START":1,"WORK_IN_PROGRESS":2}
        initial_headers = kwargs.get("headers",{})
        flag_key        = kwargs.get("flagKey","Status")
        request_fn      = kwargs.get("request_fn")
        flag_value      = initial_headers[flag_key]
        
        while(flag_value != STATUS.COMPLETED):
            response = request_fn()
            headers  = response.headers
            


    def loadMatrix(**kwargs):
        try:
            path         = kwargs.get("path")
            allow_pickle = kwargs.get("allow_pickle",False)
            xs           = np.load(path,allow_pickle=allow_pickle)
            return xs
        except Exception as e:
            print(str(e))
            raise e
    
    def getShapeOfMatrix(xs):
        xsType = type(xs)
        if(np.ndarray == xsType):
            return xs.shape
        else: 
            return np.array(xs).shape


    def downloadSaveAndLoad(**kwargs):
        try:
            Utils.downloadAndSaveFile(**kwargs)
            return Utils.loadMatrix(**kwargs)
        except Exception as e:
            print(str(e))
            raise e
            # return e
            # return None



    def downloadAndSaveFile(**kwargs):
        try:
            URL      = kwargs.get("URL")
            path     = kwargs.get("path")
            mode     = kwargs.get("mode","wb")
            response = requests.get(URL,timeout=100)
            # __________________________
            with open(path,mode) as f:
                f.write(response.content)
            return
        except Exception as e:
            print(str(e))
            raise e
            
    def downloadAndSaveFileV2(**kwargs):
        try:
            URL       = kwargs.get("URL")
            path      = kwargs.get("path")
            mode      = kwargs.get("mode","wb")
            chunkSize = kwargs.get("chunkSize",1024)
            response = requests.get(URL,timeout=100)
            # __________________________
            with open(path,mode) as f:
                for chunk in response.iter_content(chunkSize):
                    f.write(chunk)
            return 
        except Exception as e:
            print(e)
            raise e
            # f.write(response.content)

    def saveMatrix(**kwargs):
        try:
            path   = kwargs.get("path")
            matrix = kwargs.get("matrix")
            mode   = kwargs.get("mode","wb")
            # _______________________________
            with open(path,mode) as f:
                np.save(f,matrix)
            return 
        except Exception as e:
            print(e)
            raise e
            


    def generateId(**kwargs):
        prefix    = kwargs.get("prefix")
        N         = kwargs.get("random_str_len",5)
        randomStr = str(uuid4())[:N]
        return "{}{}".format(prefix,randomStr)

    def prettyprint(x):
        xs = pd.DataFrame(x)
        print(xs)

    # def initZeros(**kwargs):
    #     k = kwargs.get("k")
    #     a = kwargs.get("a")
    #     m = kwargs.get("m")
    #     Cent = []
    #     for x in range(k): 
    #         Cent.append([])
    #         for y in range(a): 
    #             Cent[x].append([])
    #             #Inicializar cent (cifrados) en 0
    #             for z in range(m): 
    #                 Cent[x][y].append(0)
    #     return Cent

    """
	description: check that the shift matrix (S) is 0
	attributes:
		S: shift matrix
	"""
    def verifyZero(S) -> bool:
        return np.all( np.array(S) ==0 )
		# temp = True
		# for t in S:
		# 	t = [0 if element==0.0 else element for element in t] #Reemplazar 0.0 por 0
		# 	temp2 = True
		# 	for u in t:
		# 		if u != 0:
		# 			temp2 = False
		# 	if not temp2:
		# 		temp = False
		# return temp
    """
    description: Generates a new set of centroids
	attributes:
		C: Set of clusters
		a: Number of attributes of D1
		k: Number of clusters
		m: number of attributes of SK
	"""
    def calculateCentroids(**kwargs):
        try:
            C          = kwargs.get("clusters")
            k          = kwargs.get("k")
            a          = kwargs.get("attributes")
            m          = kwargs.get("m")
            Liu        = kwargs.get("Liu")
            # Definir cent vacio
            cent    = np.zeros((k,a,m)).tolist()
            # _________________________________________
            for j in range(k):
                average = np.zeros((a,m)).tolist()
                
                cjLen   = len(C[j])

                if(cjLen  == 0):
                    for q in range(a):
                        cent[j][q] = np.zeros((a,m))
                else:
                    for i in range(cjLen): 
                        rec1 = C[j][i]
                        for q in range(a):
                            E1 = average[q]
                            E2 = rec1[q]
                            average[q] = Liu.add(E1,E2)
                    
                    for q in range(a):
                        v1 = 1/cjLen
                        E1 = average[q]
                        cent[j][q] = Liu.multiply_c(v1,E1)
            #  ______________________________________________________
            return cent
        except Exception as e:
            print(e)
            raise e

    """
	description: Assign remaining registers of D1 to clusters
	attributes:
		rid: record id 
		U: Updatable distance matrix
		C: Set of clusters
		D1: Encrypted dataset 
		Cent_i: conjunto de centroides
		a: Number of attributes of D1
		k: Number of clusters
	"""
    def populateClusters(**kwargs):
        try:
            rid     = kwargs.get("record_id",0)
            U       = kwargs.get("UDM")
            # _______________________________________
            C       = kwargs.get("clusters")
            # ________________________________________
            D1      = kwargs.get("ciphertext_matrix")
            D1Shape = Utils.getShapeOfMatrix(D1)
            Cent_i  = kwargs.get("centroids",None)
            a       = kwargs.get("attributes",D1Shape[1])

            def fx(**kwargs):
                limit = kwargs.get("limit")
                sim   = kwargs.get("sim")
                x,y   = kwargs.get("xy",(0,0))
                for z in range(limit):
                    sim = sim + abs(U[x][y][z])
                return sim
        
            #de k+1 al tamaño de D1
            for x in range(rid,len(D1)): 
                sim1 = []
                #desde 0 hasta k
                for y in range(len(C)): 
                    sim = 0
                    #Se revisa U completa
                    if y > x: 
                        sim = fx(limit = a, sim = sim, xy = (y,x))
                    else:
                        sim = fx(limit = a, sim = sim, xy = (x,y))
                    sim1.append(sim)
                #Se ubica el elemento con la menor distancia    
                id = sim1.index(min(sim1)) 
                #El elemento mas cercano se coloca en C
                C[id].append(D1[x]) 
            return C
        except Exception as e:
            print(e)
            raise e
            # for z in range(a): #desde 0 hasta el total de atributos
                # sim = sim + abs(U[y][x][z])

            # for z in range(a): #desde 0 hasta el total de atributos
                # sim = sim + abs(U[y][x][z])
            #     else:
            #         for z in range(a): #desde 0 hasta el total de atributos
            #             sim = sim + abs(U[x][y][z]) #Calcula la distancia entre rx y ry


    def dest_fx_vector(xs,i,x):
        xs.append(x)
        return xs
    
    def dest_fx_matrix(xs,i,x):
        xs[i].append(x)
        return xs
    """
        Arguments:
         dest: Destination list | matrix
         dest_fx: Function to perform the appending operation over destination list|matrix
         source: Source list | matrix
         limit: Number of iteration to appending elementos from source to dest.
    """
    def appends(**kwargs):
        # _
        xs      = kwargs.get("dest", [])
        dest_fx = kwargs.get("dest_fx",lambda x,i:x)
        # _
        ys  = kwargs.get("source",[])
        
        k   = kwargs.get("limit",0)
        for i in range(k):
            xs = dest_fx(xs,i,ys[i])
        return xs

    def fxTesis(*args):
        D    = args[0]
        x    = args[1]
        y    = args[2]
        z    = args[3] 
        return D[x][z] - D[y][z]
    
    def euclideanDistance(*args):
        D    = args[0]
        x    = args[1]
        y    = args[2]
        z    = args[3] 
        #return np.sqrt( (x[1] - x[0])**2 + (y[1] - y[0])**2  )
        return np.distance.euclidean(D[x][z],D[y][z])

    def create_UDM(**kwargs):
        try:
            D      = kwargs.get("plaintext_matrix")
            DShape = Utils.getShapeOfMatrix(D)
            # DShape = (3,4)
            a = kwargs.get("attributes",DShape[1])
            U = []
            # fx = self.euclideanDistance   
            fx = Utils.fxTesis    

            for x in range(DShape[0]):  # Construcción de U vacia 
                U.append([]) 
                for y in range(DShape[0]):
                    U[x].append([])
                    for z in range(a):
                        U[x][y].append([])
                        value = fx(D,x,y,z)
                        U[x][y][z]=value
            return U
        except Exception as e:
            print(e)
            raise e

    def empty_cluster(**kwargs):
        k = kwargs.get("k",3)
        return [[] for i in range(k)]