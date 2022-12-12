import random
import numpy as np
#FDH_OPE

# FDGOpe
class FDHOpe_deprecated(object):
    def keyGen(**kwargs): 
        D = kwargs.get("dataset")
        maxVal = FDHOpe_deprecated.findMax(D) #Encuentra el elemento mayor en D
        n = len(D) * len(D[0])
        maxVal = round(maxVal) + 1
        t = random.randint(4, 8)
    
        hi = 0
        mapM = {} 
        dens = []
        for i in range (t): #
            li = hi
            hi = random.uniform(0, maxVal)
            if (hi <= li):
                hi = random.uniform(li, maxVal)
            #if (hi >= maxVal):
            #   hi = random.uniform(li+1, maxVal)
            if(i == t-1):
                hi = maxVal
            mapM[i] = [li,hi]
        for i in range(t):
            dens.append(0)
        for ren in D:
            for attr in ren:
                for i in range (t):
                    val = mapM[i]
                    if (abs(attr) < val[1]):
                        dens[i] += 1
                        break
        mapC = {}
        maxValC = maxVal*7
        hpi = 0
        for i in range (t):
            lpi = hpi
            ratio = 0
            if (dens[i] == 0):
                ratio = 0.01
            else:
                ratio = dens[i]/(n*(n-1))
            leni = (maxValC * ratio)
            hpi = lpi + leni
            mapC[i] = [lpi,hpi]
        mapC[t-1] = [hpi,maxValC]
        return mapM,mapC

    def encrypt(**kwargs): #
        v     = kwargs.get("v")
        sens  = kwargs.get("sens",0.01)
        mapM  = kwargs.get("messageIntervals")
        mapC  = kwargs.get("cypherIntervals")
        t     = len(mapM)
        index = -1
        for i in range(t):
            val = mapM[i]
            if (abs(v) < val[1]):
                index = i
                break
        intervalM = mapM[index]
        intervalC = mapC[index]
        scale_i = (intervalC[1]-intervalC[0])/(intervalM[1]-intervalM[0])
        p = sens * scale_i
        delta_i = random.uniform(0,p)
        vp = intervalC[1] + scale_i * (abs(v) - intervalM[1]) + delta_i #Cambio
        if (v < 0):
            vp = vp * (-1)
        #print("vp",vp)
        return vp

 
# ________________________________________________________________
    def computePartialSens(self,val,ren,i,j):
        sens = 0
        for k in range(i,j):
            var = ren[k]
            if(abs(val-var) < sens):
                sens = abs(val-var)
        return sens

    def computeSens(self,D):
        sens = 0.01
        for i in range(len(D)):
            for j in range(len(D[0])):
                fix = D[i][j]
                for k in range(j+1, len(D[0])):
                    var = D[i][k]
                    ab = abs(fix - var)
                    if (ab < sens):
                        sens = abs(fix - var)
                for k in range(i+1,len(D)):
                    for l in range(len(D[0])):
                        var = D[k][l]
                        if (abs(fix - var) < sens):
                            sens = abs(fix - var)
        return sens

    def findMax(D):  #Obtiene el valor maximo en D para definir los intervalos
        return np.max(np.abs(np.array(D).flatten()))


class chapter5:
    
    def __init__(self,m,liu_scheme):
        self.liu_scheme=liu_scheme
        self.sk = self.liu_scheme.secretKey(m)
    
    def keyGen(self, D):
        #t = random.uniform(0,1)
        t = 4
        l,h = self.interval_limit(D)
        l, h = 0, 70 #Quitar
        space_m = self.interval_split(t, l, h)
        space_m = [0,16,26,39,70] #Quitar
        space_c = self.cipherspace(space_m)
        id = self.intervalID(space_m, 0)
        sk = self.boundary(id, space_m)
        return sk

    def max_val(self, D): #Obtiene el valor maximo en D para definir los intervalos
        maxim = 0
        for y in D:
            absolute_y = list(map(abs, y)) #pasar la lista a valores absolutos
            temp_max = max(absolute_y) #Obtener el maximo de la lista
            if (temp_max > maxim):
                maxim = temp_max
        return maxim 

    def interval_limit(self, D): #regresa los limites max y min del intervalo
        maxim = self.max_val(D)
        a =  maxim + 0.5 #Le sumo para redondear hacia arriba
        h = round(a)
        l = 0 #0 siempre va a ser el limite inferior
        return l,h
    
    def cipherspace(self, space_m): #Espacio de textos cifrados C
        razon = 3 #
        space_c = [ numero * razon for numero in space_m]    #Multiplica cada valor del espacio en m * un numero 
        return space_c

    def interval_split(self, t, l ,h): #regresa los subintervalos
        r = random.sample(range(l+1, h), t-1) #generar una lista con t-1 elementos, de l a h
        r = sorted(r) # ordenar los elementos en r
        r.insert(0, l) #insertar l al inicio 
        r.append(h) #insertar h al final
        return r 
    
    def intervalID(self, space_m, v): #regresa el intervalo en el que se encuentra v
        for i in space_m: #recorre el espacio de intervalos
            if(i <= v):
                j = i
        id = space_m.index(j)
        return id

    def boundary(self, id, space): #indica los valores que conforman el intervalo en el que se encuentra v
        li = space[id]
        hi = space[id + 1]
        return li, hi


