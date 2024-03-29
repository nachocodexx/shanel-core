import requests
from interfaces.createsecureclusteringworker import CreateSecureClusteringWorker


# Helper class
class DumbReplicator(object):
    def __init__(self,**kwargs):
        pass
    def deploy(self,**kwargs):
        return "FAKE_NODE_DEPLOYMENT"


class SecureReplicator(object):

    def __init__(self,**kws):
        self.hostname   = kws.get("hostname","localhost")
        self.port       = kws.get("port",1025)
        self.protocol   = kws.get("protocol","http")
        self.apiVersion = kws.get("apiVersion",2)
        self.url = "{}://{}:{}/api/v{}".format(self.protocol,self.hostname,self.port,self.apiVersion)
        self.createWorkerURL = "{}/generic/create".format(self.url)
        self.removeWorkerURL = lambda workerId: "{}/generic/remove/{}".format(self.url,workerId)
    
    def deploy(self,createWorker:CreateSecureClusteringWorker):
        data      = createWorker.serialize()
        response  = requests.post( self.createWorkerURL,
            data =  data, 
            headers = {
                "Content-Type":"application/json",
                "Deferred": "true"
            }
        )
        return response
    
    def remove(self,**kws):
        workerId    = kws.get("workerId")
        response = requests.post( self.removeWorkerURL(workerId))
        return response