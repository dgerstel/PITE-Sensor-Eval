#!/usr/bin/python
# -*- coding: utf-8 -*-


import numpy as np

def fuzzyRating(sensor_parameters_list, qualityFunc, norm_list=[1,1,1,1]):
    '''
    Calculates distance of a sensor under test (SUT) to a benchmark sensor

    =======
    params:
    sensor_parameters_list - list of parameters of sensor under test (SUT)
    qualityFunc - function that calculates the distance of the SUT to the benchmark sensor
    norm_list - provides normalisation of all parameters in the feature space
    '''

    # benchmark sensor params
    average_benchmark = 0.16652
    rms_benchmark = 2.717048
    skewness_benchmark = -0.019911
    kurtosis_benchmark = 0.576181

    # calculate units of parameters with the normalisation constants 
    average_unit = average_benchmark * norm_list[0]
    rms_unit = rms_benchmark * norm_list[1]
    skewness_unit = skewness_benchmark * norm_list[2]
    kurtosis_unit = kurtosis_benchmark * norm_list[3]

    # calculate distance of SUT to the benchmark sensor
    average_distance = (sensor_parameters_list[0] - average_benchmark )/average_unit
    rms_distance = (sensor_parameters_list[1] - rms_benchmark )/rms_unit
    skewness_distance = (sensor_parameters_list[2] - skewness_benchmark )/skewness_unit
    kurtosis_distance = (sensor_parameters_list[3] - kurtosis_benchmark )/kurtosis_unit

    distance = (average_distance**2 + rms_distance**2 + skewness_distance**2 + kurtosis_distance**2)**0.5

    return qualityFunc(distance)


def one_over_r(r):
    """
    quality function
    """
    return 1/r


def exp_norm(r, A=100.0, alpha=1.0):
    """
    Quality function -- normalised exp
    returns (0,A], so it doesn't have singularity at r=0,
    but returns A there.

    =======
    params:
    r - distance in the feautre space
    A - ideal sensor score
    alpha - attenuation coefficient (or sensitivity to the distance r);
            should be optimised so (nearly) all good sensors score quality >= 50 %
    """ 
    return A * np.exp(-alpha * r)


'''
sensor_data = [0.023619,2.879776,-0.065719,0.868431]

k=fuzzyRating(sensor_data,one_over_r)
print(k)

k=fuzzyRating(sensor_data,exp_norm)
print(k)

# TESTING
perfect_sensor = [0.16652, 2.717048, -0.019911, 0.576181]
almost_perfect_sensor = [0.16, 2.71, -0.019, 0.576]

#k=fuzzyRating(perfect_sensor, one_over_r)  # 1/0 !
#print(k)

k=fuzzyRating(perfect_sensor, exp_norm)
print "Perfect sensor; Q = A*exp(-alph*r): ", k, ' %'

k=fuzzyRating(almost_perfect_sensor, one_over_r)
print "Almost perfect sensor; Q = 1/r", k

k=fuzzyRating(almost_perfect_sensor, exp_norm)
print "Almost perfect sensor; Q = A*exp(-alph*r): ", k, ' %'
'''
