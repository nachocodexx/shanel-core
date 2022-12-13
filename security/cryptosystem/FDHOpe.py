import random
import numpy as np
#FDH_OPE

"""
Description: Frequency Concealment and Distribution OPE (FDH-OPE) scheme, used to facilitate the required UDM operation.
"""
class Fdhope(object):

    """
    description: generates secret keys using the FDHOPE scheme.
    """
    def keygen(**kwargs): 
        D                   = kwargs.get("dataset")
        minVal              = kwargs.get("minValue", 0)
        n_range             = kwargs.get("n_range", 4)
        proportion          = kwargs.get("proportion",3)
        maxVal_messagespace = Fdhope.findMax(D)
        maxVal_messagespace = round(maxVal_messagespace) + 1 #+1 to be able to place the last element in the range
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
        return messagespace, cipherspace
    
    """
    Description: FDH-OPE encryption algorithm
    """
    def encrypt(**kwargs):
        v            = kwargs.get("plaintext") 
        sens         = kwargs.get("sens",0.01)
        messagespace = kwargs.get("messagespace")
        cipherspace  = kwargs.get("cipherspace")
        i            = Fdhope.intervalID(v)
        li, hi         = Fdhope.boundary(i)
        lip, hip       = Fdhope.boundaryP(i)
        n_range      = kwargs.get("n_range")
        scale = (lip - hip) / (li - hi)
        tem = sens * scale
        delta = random.uniform(0,tem)
        vi = lip + scale * (abs(v) - li) + delta
        if (v < 0):
            vi = vi * (-1)
        return vi

    def calculate_dens(**kwargs):
        pass


    """
    Description: Allows you to generate keys for the defined ranges
    """
    def generate_range_keys(**kwargs):
        n_range   = kwargs.get("n_range")
        range_ids = []
        for i in range(n_range):
            id = 'RANGE_{}'.format(i)
            range_ids.append(id)
        return range_ids

    """
    Description: Generates the values of each interval depending on the defined minimum and maximum value
    """
    def generate_range_values(**kwargs):
        minValue  = kwargs.get("minValue") # Minimum value for the range
        maxValue  = kwargs.get("maxValue") # Maximum value of the ranges.
        n_range   = kwargs.get("n_range")  # Number of ranks
        range_ids = Fdhope.generate_range_keys(n_range = n_range) # Generate array of ids
        r         = round( (maxValue) / n_range) # Range length approximation
        rangos = {} # Dictionary for ranges
        
        for index,range_id in enumerate(range_ids): 
            minVal = index * r
            maxVal = maxValue+1 if (index == n_range-1) else minVal + r
            rangos[ range_id ] = (minVal, maxVal)
        return rangos

    """
    Description: It allows to find the maximum value of the dataset 
    """
    def findMax(D):  #Obtiene el valor maximo en D para definir los intervalos
        return np.max(np.abs(np.array(D).flatten()))

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

if __name__ == "__main__":
    plaintext_matrix = [
        [0.73,8.84],
        [49.93,34.44],
        [0.57,65.04],
        [62.15,32.29],
        [59.47,36.04]
    ]
    Fdhope.keygen(dataset = plaintext_matrix)