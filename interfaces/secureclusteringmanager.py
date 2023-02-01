import requests
import json
# Helper class
class Text(object):
    def __init__(self,**kwargs):
        workerId = kwargs.get("workerId")
        self.text = json.dumps({"workerId":workerId})

class DumbSecureClusteringManager(object):
    def __init__(self):
        pass
        
    def sendSecureClusteringRequest(self,**kwargs):
        return Text(workerId = kwargs.get("workerId","localhost"))
"""
Description: 
    Class that allows the connection between the client and the manager
Attributes: 
    hostname, port
    available ports:
        Client  -> 3000-5999
        Manager -> 6000-8999
        Workers -> 9000+
"""
class SecureClusteringManager(object):
    def __init__(self,**kwargs):
        self.hostname      = kwargs.get("hostname","localhost")
        self.port          = kwargs.get("port",6000)
        self.protocol      = kwargs.get("protocol","http")
        self.apiVersion    = kwargs.get("apiVersion",2)
        
        # <protocol>://<hostname|ip>:<port>
        self.baseUrl       = "{}://{}:{}".format(self.protocol,self.hostname,self.port)
        self.clusteringURL = "{}/clustering/secure".format(self.baseUrl)
    
    """
    Description:
        Function that allows sending the data with the request 
    Notes:
        serialize(): convert a value to a sequence of bits to be transmitted across a network.
    """
    def sendSecureClusteringRequest(self,**kwargs):
        data     = kwargs.get("data")
        _data    = data.serialize()
        response = requests.post(
            self.clusteringURL,
            data = _data,
            headers= {"Content-Type":"application/json"}
        )
        return response

