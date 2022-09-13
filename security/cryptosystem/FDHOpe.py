import random
import numpy as np
#FDH_OPE

# FDGOpe
class FDHOpe(object):
    def keyGen(**kwargs): 
        D = kwargs.get("dataset")
        maxVal = FDHOpe.findMax(D) #Encuentra el elemento mayor en D
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
        mapM  = kwargs.get("messageIntervals") # message Interval
        mapC  = kwargs.get("cypherIntervals") # cipher Interval
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
        return vp

    def findMax(D):
        return np.max(np.abs(np.array(D).flatten()))
        # max = 0
        # for ren in D:
        #     for val in ren:
        #         if(abs(val) > max):
        #             max = abs(val)
        # return max

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

