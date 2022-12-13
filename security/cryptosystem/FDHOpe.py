import random
import numpy as np
#FDH_OPE

# FDGOpe 
class Fdhope(object):
    def keygen(**kwargs): 
        D                   = kwargs.get("dataset")
        minVal              = kwargs.get("minValue", 0)
        n_range             = kwargs.get("n_range", 4)  #Se puede cambiar
        proportion          = kwargs.get("proportion",3)
        maxVal_messagespace = Fdhope.findMax(D)
        maxVal_messagespace = round(maxVal_messagespace) + 1
        
        maxVal_cipherspace  = maxVal_messagespace * proportion

        messagespace = Fdhope.generate_range_values(
            minValue = minVal, 
            maxValue = maxVal_messagespace, 
            n_range  = n_range
        )
        

        cipherspace  = Fdhope.generate_range_values(
            minValue = minVal,
            maxValue = maxVal_cipherspace,
            n_range  = n_range
        )

        print(messagespace)
        print(cipherspace)
    
    def generate_range_keys(**kwargs):
        n_range = kwargs.get("n_range")
        range_ids= []
        for i in range(n_range):
            id = 'RANGE_{}'.format(i)
            range_ids.append(id)
        return range_ids

    def generate_range_values(**kwargs):
        #  Arreglo de ids
        minValue = kwargs.get("minValue")
        #  Valor maximo de los rangos.
        maxValue    = kwargs.get("maxValue") 
        #  Cantidad de rangos
        n_range   = kwargs.get("n_range")
        range_ids = Fdhope.generate_range_keys(n_range = n_range)
        #  Aprox. de longitud del rango 
        r         = round( (maxValue) / n_range) 
        rangos = { }
        #gen_range = lambda minValue,maxValue: list(range(minValue,maxValue))
        for index,range_id in enumerate(range_ids): 
            minVal = index * r
            maxVal = maxValue+1 if (index == n_range-1) else minVal + r 
            # List => [ ]
            # Tuple => ( )
            rangos[ range_id ] = (minVal, maxVal)
        return rangos

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


if __name__ == "__main__":
    plaintext_matrix = [
        [0.73,8.84],
        [49.93,34.44],
        [0.57,65.04],
        [62.15,32.29],
        [59.47,36.04]
    ]
    Fdhope.keygen(dataset = plaintext_matrix)