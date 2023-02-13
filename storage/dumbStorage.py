import numpy as np

class DumbStorage(object):
    def get_matrix(self,**kwargs):
        return ({
            'tags':{
                'dtype':"float",
                'shape':(5,5)
            }
        },
        np.zeros(5,5)
        )
    
    def put_matrix(self,**kwargs):
        return None