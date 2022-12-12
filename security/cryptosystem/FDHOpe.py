import random
import numpy as np
#FDH_OPE

# FDGOpe
class FDHOpe_deprecated(object):
    def keyGen(**kwargs): 
        pass

    def findMax(D):  #Obtiene el valor maximo en D para definir los intervalos
        return np.max(np.abs(np.array(D).flatten()))
