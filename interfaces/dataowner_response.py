import numpy as np
import json
from requests import Response

"""
Description: Interface used for the expected result of the dataowner
"""
class DataownerResponse(object):
	def __init__(self,**kwargs):
		self.labelVector  = kwargs.get("labelVector",[])
		self.serviceTime  = kwargs.get("serviceTime",0)
		self.responseTime = kwargs.get("responseTime",0)
		self.algorithm    = kwargs.get("algorithm",None)
		self.headers      = kwargs.get("headers",{})
		self.status       = kwargs.get("status",0)
	
	def fromResponse(response:Response):
		jsonString = response.content.decode("utf-8")
		jsonResponse = json.loads(jsonString)
		jsonResponse["labelVector"] = np.array(jsonResponse.get("labelVector",[]))

		return DataownerResponse(
			**jsonResponse, 
			headers = response.headers,
		    status = response.status_code
		)

