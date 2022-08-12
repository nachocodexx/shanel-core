import requests

class SecureClusteringManager(object):
    def __init__(self,**kwargs):
        # _____________________________________________________
        self.hostname      = kwargs.get("hostname","localhost")
        self.port          = kwargs.get("port",6000)
        # _____________________________________________________
        self.protocol      = kwargs.get("protocol","http")
        # _____________________________________________________
        self.apiVersion    = kwargs.get("apiVersion",2)
        # _____________________________________________________
        # <protocol>://<hostname|ip>:<port>
        self.baseUrl       = "{}://{}:{}".format(self.protocol,self.hostname,self.port)
        # _____________________________________________________
        self.clusteringURL = "{}/clustering/secure".format(self.baseUrl)
        # _____________________________________________________
    
    def sendSecureClusteringRequest(self,**kwargs):
        data     = kwargs.get("data")
        _data    = data.serialize()
        
        # __________________________________
        response = requests.post(
            self.clusteringURL,
            data = _data,
            headers= {"Content-Type":"application/json"}
        )
        # _________________________________
        return response

