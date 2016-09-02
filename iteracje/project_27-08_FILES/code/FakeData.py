#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import random
import math
from sklearn.neighbors import KNeighborsClassifier
from sklearn import cross_validation

def generateFakeData(sourcepath, fake_data_path, p_value_list, samples, append=False):
    """
    Generates simulated bad-quality sensor data (parameters in feature space) based on good-quality real sensor data.
    It is done by departing from good-quality sensor params TO SOME EXTENT

    =======
    params:
    sourcepath - points to the file with feature-space parameters and class; one row per sensor
    fake_data_path - output path for the fake data
    samples - number of fake samples to be created
    append - whether to append or overwrite the output file with fake data
    p_value_list - ??
    """

    # load original (real) sensor data (42 samples)
    from_sensors = np.loadtxt(sourcepath, delimiter=",")
    
    # calculate mean and std. dev. among all rows for each parameter
    average_list = [i[0] for i in from_sensors]
    average_par = (np.average(average_list),np.std(average_list))
    rms_list = [i[1] for i in from_sensors]
    rms_par = (np.average(rms_list),np.std(rms_list))
    skewness_list = [i[2] for i in from_sensors]
    skewness_par = (np.average(skewness_list),np.std(skewness_list))
    kurtosis_list = [i[3] for i in from_sensors]
    kurtosis_par = (np.average(kurtosis_list),np.std(kurtosis_list)) 

    # simulate bad quality sensors by randomly departing from good quality sensor parameters
    # each parameter x gets mean_x +/- p * stddev_x, where p is from (p_value_list[i][0], p_value_list[i][1]) range
    result = []
    for i in range(samples):
        random_data = [average_par[0] + random.choice([1,-1]) * random.uniform(p_value_list[0][0] * average_par[1], p_value_list[0][1] * average_par[1]),
                       rms_par[0] + random.choice([1,-1]) * random.uniform(p_value_list[1][0]*rms_par[1],p_value_list[1][1]*rms_par[1]),
                       skewness_par[0] + random.choice([1,-1]) * random.uniform(p_value_list[2][0]*skewness_par[1],p_value_list[2][1]*skewness_par[1]),
                       kurtosis_par[0] + random.choice([1,-1]) * random.uniform(p_value_list[3][0]*kurtosis_par[1],p_value_list[3][1]*kurtosis_par[1]),
                       0]
        result.append(random_data)

    # save result to output file (either append or overwrite)
    # write mode
    if append:
        write_mode = 'a'
    else:
        write_mode = 'w'

    with open(fake_data_path, write_mode) as fake_file:
        np.savetxt(fake_file, result, delimiter=",", fmt='%.7f', newline='\n')
    saved_value = np.loadtxt(fake_data_path, delimiter=",")


class KNN():
	def __init__(self,fakedatapath, sensordatapath, n_sensor_samples=None, n_fake_samples=None):
            """
            Read the data from real sensors and simulated fake data.
            Analysis may be limited to n_sensor_samples and n_fake_samples if desired

            =======
            params:
            fakedatapath
            sensordatapath
            n_sensor_samples - number of rows to be analysed from the sensor data file
            n_fake_samples - number of rows to be analysed from the fake data file
            """

            self.from_sensors = np.loadtxt(sensordatapath, delimiter=",")  #  42 rows
            self.fake_data = np.loadtxt(fakedatapath, delimiter=",")

            #TODO: code: take only n_sensor(fake)_samples; do it randomly
            if n_sensor_samples is not None:
                pass

            if n_fake_samples is not None:
                pass


	def TrainAndPredict(self, k=3, train_test_ratio=0.3, weights='distance', metric='minkowski', algorithm='auto'):
                """
                Trains k-nearest neighbours classifier with sensor and simulated (fake) data and checks accuracy of the classifier
                by comparing its predictions with test samples in two ways: directly and using cross-validation

                =======
                params:
                k - number of neighbours
                train_test_ratio - specifies how many samples use for training the algorithm and how many for testing its accuracy
                weights - pertains to data points (NOT to the attributes!); the closer ones may be regarded as more important (weights='distance');
                          possible weights: 'uniform', 'distance', [callable].
                          The [callable] is a user-defined function
                algorithm - 'auto'; shan't be changed in this little project
                metric - e.g. 'minkowski' or 'euclidean' or 'mahalanobis' tells the algorithm how to measure the distance
                """

                # how many rows for training
                num_sensor_train = int(train_test_ratio * len(self.from_sensors))
                num_fake_train = int(train_test_ratio * len(self.fake_data))

                traindata = np.concatenate((self.from_sensors[:num_sensor_train, :-1], self.fake_data[:num_fake_train, :-1]), axis=0)
		targetvalues = [1 for i in range(num_sensor_train)] + [0 for i in range(num_fake_train)] # array of 0/1
                # TODO: dictionary looks better than lists alone

                # build a classifier and teach it
		self.neigh = KNeighborsClassifier(n_neighbors=k, weights=weights, algorithm=algorithm, metric=metric)
		self.neigh.fit(traindata, targetvalues)

                # check accuracy with cross-validation
                # TODO: shuffle split is not bad, but not perfect - it may take same thing as different subsets(!);
                # it's better to find an alternative method from cross_validation class
		cv = cross_validation.ShuffleSplit(len(targetvalues), n_iter=10, test_size=10, random_state=0)
		self.knn_score = cross_validation.cross_val_score(self.neigh, traindata, targetvalues, cv=cv)
		
                # summarise all test data (predictions)
                print "------All params @: {"
                print "n_neighbors: " + str(k) + "  train_test_ratio: " + str(train_test_ratio) + "  weights: " + str(weights) + "  metric: "+str(metric) + "  algorithm: "+str(algorithm) + " }"
                print "Sensor data prediction: (1 = good, 0 = bad)" + str(self.neigh.predict(self.from_sensors[num_sensor_train:, :-1]))
                print "Fake data prediction:" + str(self.neigh.predict(self.fake_data[num_fake_train:, :-1])) 
                print "Probability of correct assessment (sensor data):"
                print "[1st column: bad | 2nd column: good]"
                print str(self.neigh.predict_proba(self.from_sensors[num_sensor_train:, :-1]))
                print "Probability of correct assessment (fake data): \n" + str(self.neigh.predict_proba(self.fake_data[num_fake_train:, :-1]))



