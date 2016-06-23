from __future__ import print_function
import sys
import os

from pyspark import SparkContext
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionWithSGD
from pyspark.mllib.linalg import _convert_to_vector
from numpy import *


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("Usage: python runFlayypBirdServer.py")
        exit(-1)
    
    sc = SparkContext(appName="FlappyBird-DQN")
    cfgFile = sc.textFile("saved_networks/checkpoint")
    lineLengths = cfgFile.map(lambda s: len(s))
    totalLength = cfgFile.reduce(lambda a, b: a + b)

    cmdline = "python flappyBirdRemote.py"
    os.system(cmdline)
    
    sc.stop()
