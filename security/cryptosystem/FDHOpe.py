import random
import numpy as np
#FDH_OPE

# FDGOpe
class fdhope(object):
    def keyGen(**kwargs): 
        D = kwargs.get("dataset")
       

    def intervalLimit(**kwargs):
        maxVal = fdhope.findMax(D)
        maxVal = round(maxVal) + 1
    

    def intervalID(**kwargs):
        # |v|
        pass
        #return i

    def boundary(**kwargs):
        #i
        pass
        #return li, hi

    def boundaryP(**kwargs):
        #i
        pass
        #return lip, hip

    def findMax(D):  #Obtiene el valor maximo en D para definir los intervalos
        return np.max(np.abs(np.array(D).flatten()))


