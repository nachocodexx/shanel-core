from time import time
from utils.Utils import Utils
from sklearn.cluster import KMeans
from interfaces.clustering_result import ClusteringResult

def kmeans(**kwargs):
    startTime            = time()
    k                    = kwargs.get("k",2)
    plain_matrix         = kwargs.get("plaintext_matrix")
    centroids            = Utils.generate_centroids(k = k,plain_matrix = plain_matrix)
    start_service_time   = time()
    kmeans               = KMeans(n_clusters=k,init=centroids)
    kmeans.fit(plain_matrix)
    end_service_time     = time()
    service_time = end_service_time - start_service_time
    response_time        = time() - startTime
    
    return ClusteringResult(
        labels_vector = kmeans.labels_,
        n_iterations  = kmeans.n_iter_,
        response_time = response_time,
        service_time  = service_time
    )
    
    # return {
    #      "labels_vector"     :kmeans.labels_,
    #      "n_iterations" :kmeans.n_iter_,
    #      "response_time"     :response_time,
    #      "service_time"      :service_time,
    # }