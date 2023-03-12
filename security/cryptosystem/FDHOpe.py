import random
import numpy as np
from collections import Counter
from utils.Utils import Utils
from time import time
from interfaces.cipherscheme_result import CipherschemeResult

"""
Description: 
    A class to represent Frequency Concealment and Distribution OPE (FDH-OPE) scheme, 
    used to facilitate the required UDM operation.
"""
class Fdhope(object):
    """
    description: generates secret keys using the FDHOPE scheme.
    attributes: 
        minVal: number where the space will start
        max_range: maximum number of ranges that can be in the space
        proportion: indicates how much the encrypted space will grow in relation to the message space
    """
    def keygen(**kwargs): 
        dataset              = kwargs.get("dataset") #Cambiar nombre de variable
        minVal               = kwargs.get("minValue", 0)
        max_range            = kwargs.get("max_range",8)
        proportion           = kwargs.get("proportion", 5)
        Dshape               = Utils.getShapeOfMatrix(dataset)
        maxVal_messagespace  = round(Fdhope.findMax(dataset)) + 2 #+1 to be able to place the last element in the range
        maxVal_cipherspace   = maxVal_messagespace * proportion #indicates how much it grows with respect to the message space
        lenTriangle          = Dshape[0] * Dshape[1] #size of the lower interval of U
        n_range              = random.randint(3,max_range) #Number of ranges created
        messagespace,new_density = {}, {}

        _messagespace = Fdhope.generate_range_values( #Generate possible message space
            minValue = minVal, 
            maxValue = maxVal_messagespace, 
            n_range  = n_range
        )
        old_density  = Fdhope.calculate_dens( #Calculates the amount of data that is in each range
            dataset            = dataset, 
            messagespace       = _messagespace, 
            maxVal_cipherspace = maxVal_cipherspace
        )
        
        messagespace_filtered = dict(list(filter(lambda x: old_density.get(x[0],0) > 0, _messagespace.items()))) #Remove ranges where no data exists
        messagespace_list     = list(messagespace_filtered.items()) #Convert messagespace to list

        global_max = -1
        for index,key in enumerate(messagespace_filtered): #iterate through the new message space
            new_key                 = "RANGE_{}".format(index) # 
            message_space_pair      = messagespace_list[index] # Locate the element to be analyzed (RANGE_ID -> TUPLE_RANGE)
            old_key                 = message_space_pair[0] # Value in density[key]
            new_density[new_key]    = old_density[old_key]  # 
            rango                   =  message_space_pair[1] # tuple with minimum and maximum of that range
            current_min,current_max = rango
            if(index == 0 or current_min <= global_max):
                global_max = current_max
                messagespace[new_key] = (current_min,current_max)#
            else:
                if(current_min > global_max):
                    messagespace[new_key] = (global_max,current_max)#
                    global_max            = current_max
            
        index_maxmessagespace = len(messagespace)-1
        index_maxrange = "RANGE_{}".format(index_maxmessagespace)
        tuple_maxrange = (messagespace[index_maxrange][0],maxVal_messagespace)
        messagespace[index_maxrange] = tuple_maxrange

        intervalLength = Fdhope.calculate_intervalLength( #Calculates the size of the intervals for the ciphertextspace
            density            = new_density, 
            lenTriangle        = lenTriangle, 
            maxVal_cipherspace = maxVal_cipherspace
        )
        cipherspace  = Fdhope.generate_range_values( #Generate cipher space
            minValue      = minVal,
            maxValue      = maxVal_cipherspace,
            n_range       = len(intervalLength), #New range size
            range_ids     = intervalLength.keys(), #Extract keys to intervalLength
            ranges_values = np.cumsum([0] + list(intervalLength.values())) #Make the cumulative sum of the elements in intervalLength
        )
        return messagespace, cipherspace
        
    def encryptMatrix(**kwargs):
        start_time = time()
        plaintext_matrix = kwargs.pop("plaintext_matrix")
        xs = []
        for plaintext_vector in plaintext_matrix:
            x = Fdhope.encryptVector(
                plaintext_vector = plaintext_vector,
                **kwargs
            )
            xs.append(x)
        end_time   = time()
        encryption_time = end_time-start_time
        
        return CipherschemeResult(
			matrix         = xs, 
			time           = encryption_time,
			operation_type = "encrypt_fdhope"
		)

    def encryptVector(**kwargs):
        plaintext_vector = kwargs.pop("plaintext_vector")
        xs = []
        for plaintext in plaintext_vector:
            x = Fdhope.encrypt(
                plaintext = plaintext,
                **kwargs
            )
            xs.append(x)
        return xs

    """
    Description: allows you to encrypt a plaintext using the previously generated keys, applying the FDHOPE encryption algorithm
    Attributes:
        plaintext: value to encrypt
        sens: is the smallest difference value between two plaintexts
        messagespace: full message space in which the dataset values are found
        cipherspace: full cipher space in which the dataset values are found
    """
    def encrypt(**kwargs):
        plaintext    = kwargs.get("plaintext") 
        sens         = kwargs.get("sens",0.01)
        messagespace = kwargs.get("messagespace")
        cipherspace  = kwargs.get("cipherspace")
        interval_id = Fdhope.getIntervalID( #returns the id of the range in which the plaintext is found
            plaintext    = plaintext, 
            messagespace = messagespace
        )

        messagespace_min, messagespace_max = Fdhope.getBoundary( #given the id, it returns the minimum and maximum value of that space.
            interval_id = interval_id, 
            space       = messagespace
        )
        
        cipherspace_min, cipherspace_max = Fdhope.getBoundary( #given the id, it returns the minimum and maximum value of that space.
            interval_id = interval_id, 
            space       = cipherspace,
        )

        scale      = (cipherspace_min - cipherspace_max) / (messagespace_min - messagespace_max) #
        delta      = random.uniform(0,sens * scale) #value that allows to give randomness to the ciphertext
        ciphertext = cipherspace_min + scale * (abs(plaintext) - messagespace_min) + delta # ciphertext generated

        if (plaintext < 0): #if the plaintext is negative
            ciphertext = ciphertext * (-1) #the ciphertext preserves the sign of the plaintext       
        return ciphertext


    """
    Description: Counts elements that belong to each defined range
    """
    def calculate_dens(**kwargs):
        dataset            = kwargs.get("dataset")
        Dshape             = Utils.getShapeOfMatrix(dataset)
        messagespace       = kwargs.get("messagespace")
        dens               = []
        for plaintext_matrix in dataset:
            for plaintext_vector in plaintext_matrix:
                if len(Dshape) == 3: #in the case of an EU matrix, it has one more dimension
                    for plaintext in plaintext_vector:
                        key = Fdhope.getIntervalID( #returns the id of the range in which the plaintext is found
                            plaintext = plaintext, 
                            messagespace = messagespace
                            )
                        dens.append(key)
                elif len(Dshape) == 2: #in the case of an ED matrix
                    key = Fdhope.getIntervalID( #returns the id of the range in which the plaintext is found
                        plaintext = plaintext_vector, 
                        messagespace = messagespace
                        )
                    dens.append(key)
                else:
                    raise Exception("dimension error")
        conteo = Counter(dens) #calculate the number of items found
        return dict(conteo.items()) #save conteo as dictionary


    """
    Description: Calculate the jump for each of the cipherspace ranges
    """
    def calculate_intervalLength(**kwargs):
        density            = kwargs.get("density",{})
        lenTriangle        = kwargs.get("lenTriangle",1)
        maxVal_cipherspace = kwargs.get("maxVal_cipherspace")
        intervalLenght     = {}
        for key, value in density.items():
            ratio               = value/lenTriangle
            il                  = maxVal_cipherspace * ratio
            intervalLenght[key] = round(il)
        return intervalLenght


    """
    Description: Allows to generate ids for the defined ranges
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
        minValue      = kwargs.get("minValue") # Minimum value for the range
        maxValue      = kwargs.get("maxValue") # Maximum value of the ranges.
        n_range       = kwargs.get("n_range")  # Number of ranks
        range_ids     = kwargs.get("range_ids",Fdhope.generate_range_keys(n_range = n_range)) # Generate array of ids
        ranges_values = kwargs.get("ranges_values",[minValue] + sorted([np.random.uniform(minValue+0.2,maxValue) for _ in range(n_range-1)]) + [maxValue]) #Generate random ranges values
        rangos        = {} # Dictionary for ranges
        for index,range_id in enumerate(range_ids):
            minVal           = ranges_values[index]
            maxVal           = maxValue+1 if (index == n_range-1) else ranges_values[index+1]
            rangos[range_id] = (minVal, maxVal)  #Diccionario Rangos, key = range_id, value = tuple
        return rangos


    """
    Description: It allows to find the maximum value of the dataset 
    """
    def findMax(D):  #Obtiene el valor maximo en D para definir los intervalos
        return np.max(np.abs(D.flatten()))


    """
    Description: Returns the ID of the range in which the element is found
    """
    def getIntervalID(**kwargs):
        plaintext    = abs(kwargs.get("plaintext",0))
        messagespace = kwargs.get("messagespace")
        for key, value in messagespace.items():
            if (plaintext >= value[0] and plaintext < value[1]):
                return key
        

    """
    Description: Given "range_id" get min and max of message space
    """
    def getBoundary(**kwargs):
        interval_id = kwargs.get("interval_id")
        space       = kwargs.get("space")   
        value       = space.get(interval_id)
        li          = value[0]
        hi          = value[1]

        
        
        return li, hi
        

if __name__ == "__main__":
    # plaintext_matrix = [
    #     [0.73,8.84],
    #     [49.93,34.44],
    #     [0.57,65.04],
    #     [62.15,32.29],
    #     [59.47,36.04]
    # ]
    plaintext_matrix = np.random.uniform(low=0,high=1, size=(5,2))
    plaintext_matrix = np.array(plaintext_matrix)
    messagespace, cipherspace = Fdhope.keygen(
        dataset = plaintext_matrix, 
        n_range = 4, 
        proportion = 3
    )
    print("Message space",messagespace)
    print("Cipher space",cipherspace)

    ciphertext_matrix = Fdhope.encryptMatrix(
        plaintext_matrix = plaintext_matrix,
        sens         = 0.001,
        messagespace = messagespace,
        cipherspace  = cipherspace
    )
    
    #ciphertext = Fdhope.encrypt(
    #    plaintext    = 34.44,
    #    sens         = 0.01,
    #    messagespace = messagespace,
    #    cipherspace  = cipherspace
    #    )
    print(ciphertext_matrix.matrix)
