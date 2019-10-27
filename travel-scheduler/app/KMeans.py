import numpy as np
class KMeans:
    def __init__(self, k=3, tol=0.001, max_iter=2):
        self.k = k
        self.tol = tol
        self.max_iter = max_iter

    def avg(self, lst):
        lats = []
        lons = []
        for item in lst:
            lat, lon = item.split(', ')
            lats.append(float(lat))
            lons.append(float(lon))
        lats = np.array(lats).astype(np.float)
        lons = np.array(lons).astype(np.float)
        return str(np.mean(lats)) + "," + str(np.mean(lons))

    def fit(self,data):

        self.centroids = {}
        print(data)
        for i in range(self.k):
            self.centroids[i] = data[i].pos

        for i in range(self.max_iter):
            self.classifications = {}
            self.classification_names = {}

            for i in range(self.k):
                self.classifications[i] = []
                self.classification_names[i] = []

            for featureset in data:
                distances = [featureset.calc_dist_from_center(self.centroids[centroid]) for centroid in self.centroids]
                print(distances)
                # distances = [featureset.calc_dist_from_center(featureset.pos, self.centroids[centroid]) for centroid in self.centroids]
                classification = distances.index(min(distances))
                self.classification_names[classification].append(featureset)
                self.classifications[classification].append(featureset.pos)

            prev_centroids = dict(self.centroids)

            for classification in self.classifications:
                self.centroids[classification] = self.avg(self.classifications[classification])
