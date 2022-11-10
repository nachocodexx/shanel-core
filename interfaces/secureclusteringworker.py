from requests import Session,Response


class SecureClusteringWorker(object):
    def __init__(self,**kwargs):
        self.workerId  = kwargs.get("workerId")
        self.port      = kwargs.get("port",9000)
        self.session   = kwargs.get("session")
        self.algorithm = kwargs.get("algorithm","SK_MEANS")
    

    def run(self,*args,**kwargs) -> Response:
        operationIndex = kwargs.get("operationIndex",1)
        # 
        if(self.algorithm == "SK_MEANS"):
            return  self.SKMeans_1(**kwargs) if(operationIndex==1) else self.SKMeans_2(**kwargs)
        elif(self.algorithm =="KMEANS"):
            return self.kmeans(**kwargs)
        elif (self.algorithm == "DBSKMEANS"): 
            return self.DBSkMeans(**kwargs)
        else:
            return Response(None,503)

    

    def kmeans(self,**kwargs) -> Response:
        return self.session.post(
            "http://{}:{}/clustering/kmeans".format(self.workerId,self.port),
             headers = kwargs,
            #  timeout = timeout
        )

    def DBSkMeans(self,**kwargs):
        return Response()

    # { a: 1 } + {b: 2} = {a:1,b:2}
    # { **{a:1},**{b:2,c:3} } = {a:1,b:2,c:3}
    def SKMeans_1(self,**kwargs) -> Response:
        timeout = kwargs.pop("timeout",None)
        return self.session.post(
            "http://{}:{}/clustering/skmeans/1".format(self.workerId,self.port),
             headers = kwargs,
             timeout = timeout
        )

    def SKMeans_2(self,**kwargs) -> Response:
        timeout = kwargs.pop("timeout",None)
        return self.session.post(
            "http://{}:{}/clustering/skmeans/2".format(self.workerId,self.port),
             headers = kwargs,
             timeout = timeout
        )
        # self.