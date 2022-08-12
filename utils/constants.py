
class Constants(object):
    class ClusteringStatus(object):
        COMPLETED        = 0
        START            = 1
        WORK_IN_PROGRESS = 2
    class ClusteringAlgorithms(object):
        SK_MEANS   = "SK_MEANS"
        DBSK_MEANS = "DBSK_MEANS"