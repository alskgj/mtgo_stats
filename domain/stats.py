import numpy
import scipy


def mean_confidence_interval(data, confidence=0.95):
    data = 1.0 * numpy.array(data)
    mean, standard_error = numpy.mean(data), scipy.stats.sem(data)
    confidence = standard_error * scipy.stats.t.ppf((1 + confidence) / 2., len(data)-1)
    return round(mean, 2), round(mean-confidence, 2), round(mean+confidence, 2)


def test_mean_confidence_interval():
    data = [0.5, 0.55, 0.6, 0.6]
    mean, lower, upper = mean_confidence_interval(data)
    assert 0.56 == mean
    assert 0.49 == lower
    assert 0.64 == upper
