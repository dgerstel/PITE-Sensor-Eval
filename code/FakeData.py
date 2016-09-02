#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import random
import math

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


