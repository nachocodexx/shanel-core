from validationindex.validationindex import dunn_fast
from sklearn.metrics import silhouette_score,davies_bouldin_score,calinski_harabasz_score
from sklearn.metrics import adjusted_mutual_info_score,fowlkes_mallows_score,adjusted_rand_score,jaccard_score


def internal_validation_indexes(**kwargs):
    plaintext_matrix = kwargs.get("plaintext_matrix")
    target           = kwargs.get("target")
    score_silhouette = silhouette_score(plaintext_matrix, target, metric='euclidean')
    davies_bouldin   = davies_bouldin_score(plaintext_matrix, target)
    calinski_harabaz = calinski_harabasz_score(plaintext_matrix, target)
    dunn             = dunn_fast(plaintext_matrix,target)
    return {
         "silhouette_coefficient" : score_silhouette,
         "davies_bouldin_index"   : davies_bouldin,
         "calinski_harabaz_index" : calinski_harabaz,
         "dunn_index"           : dunn,
    }
    
def external_validation_indexes(**kwargs):
    pred   = kwargs.get("pred")
    target = kwargs.get("target")
    k      = kwargs.get("k")
    # variable = expression 
    avg    = 'binary' if (k==2) else 'micro'
    mutual_info_adjusted = adjusted_mutual_info_score(target, pred)
    fowlkes_mallows      = fowlkes_mallows_score(target, pred)
    adjusted_rand        = adjusted_rand_score(target, pred) 
    jaccard              = jaccard_score(target, pred, average=avg)
    return {
         "adjusted_mutual_information" : mutual_info_adjusted,
         "fowlkes_mallows_index"       : fowlkes_mallows,
         "adjusted_rand_index"         : adjusted_rand,
         "jaccard_index"               : jaccard
    }