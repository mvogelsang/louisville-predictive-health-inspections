from scipy import stats
import subprocess
import os
import sqlite3
import datetime
import sqlQueries
import time
import sklearn
from sklearn import preprocessing, metrics, model_selection, linear_model, svm, neural_network
import pyglmnet
import numpy
import math
import pickle
from fpdf import FPDF
import warnings
warnings.filterwarnings('ignore')


# note, for convenience of writing many separate query functions
# the connection is defined globally
dbConn = sqlite3.connect("./LouData.db", detect_types=sqlite3.PARSE_DECLTYPES);
# dbConn.row_factory = sqlite3.Row
dbCursor = dbConn.cursor()
dbCursor.executescript(sqlQueries.E_speedConfigure_0)

def getModelTrainingInput():
    dbCursor.execute(sqlQueries.G_modelTrainingInput_0)
    data = dbCursor.fetchall()
    return numpy.array(data)

def getModelTrainingOutput():
    dbCursor.execute(sqlQueries.G_modelTrainingOutput_0)
    temp = dbCursor.fetchall()

    # flatten the list of tuples received
    flattened = list(sum(temp, ()))
    return numpy.array(flattened)

def getglmnet():
    return pyglmnet.GLM(distr='gaussian', alpha=0.05, score_metric='pseudo_R2')

def getStandardScaler(trainingInput):
    scaler = preprocessing.StandardScaler()
    scaler.fit(trainingInput)
    return scaler

def getTestPredictions(testInput, analysisTool, predictsAnArray):
    if predictsAnArray:
        predictions = []
        for datapoint in testInput:
            predictions.append(numpy.mean(analysisTool.predict(datapoint)))
    else:
        predictions = analysisTool.predict(testInput)

    return predictions

def fitEstimator(tool, paramDict, trainingInput, trainingOutput, totalTries=5):
    # track time taken to run search
    start = time.time()
    newTool = model_selection.RandomizedSearchCV(estimator=tool, param_distributions=paramDict, cv=3, refit=True, n_iter=totalTries, n_jobs=4, verbose=0)
    newTool.fit(trainingInput, trainingOutput)
    end = time.time()
    delta = end-start
    print '\t HyperParameter Search done in ' + str(delta) + 'seconds'
    print '\t ' + str(float(delta)/float(totalTries)) + ' seconds per parameter combination'
    print '\t best params - ' + str(newTool.best_params_)
    return newTool.best_estimator_

def main():

    # get the necessary components to build and use an analysis tool
    print( 'getting input...')
    tInput = getModelTrainingInput()
    print( 'getting output...')
    tOutput = getModelTrainingOutput()
    if len(tInput) != len(tOutput):
        print( 'WARNING training input/output mismatch')

    # get scaler and standardize the input data
    print( 'scaling...')
    scaler = getStandardScaler(tInput)
    tInput = scaler.transform(tInput)
    tInputSmall = tInput[-10000:]
    tOutputSmall = tOutput[-10000:]

    # get a test input and output set
    print( 'creating data subsets..')
    prelimInput = tInputSmall[-1000:-500]
    prelimOutput = tOutputSmall[-1000:-500]
    testInput = tInputSmall[-500:]
    testOutput = tOutputSmall[-500:]

    # get and pre-train each tool
    print( 'getting tools...')
    print( '\tglm...')
    glmnet = getglmnet()
    glmnet.fit(prelimInput,prelimOutput)


    print '\tsvr...'
    svrRegressorDict = {'C': numpy.arange(.1,10,.1), }
    svrRegressor = fitEstimator( svm.LinearSVR(), svrRegressorDict, prelimInput, prelimOutput, 75)

    print '\tard...'
    ardRegressorDict = {'alpha_1': numpy.arange(1.e-6, 1.e-5, 1.e-6), 'alpha_2': numpy.arange(1.e-6, 1.e-5, 1.e-6)}
    ardRegressor = fitEstimator(linear_model.ARDRegression(), ardRegressorDict, prelimInput, prelimOutput, 10)

    print '\tmlp...'
    mlpRegressorDict = {'hidden_layer_sizes':[(1),(2),(3),(len(prelimInput[0])/2)], 'learning_rate': ['constant', 'invscaling', 'adaptive'], 'solver': ['lbfgs', 'sgd', 'adam'], 'activation': ['identity', 'relu']}
    mlpRegressor = fitEstimator(neural_network.MLPRegressor(), mlpRegressorDict, tInputSmall, tOutputSmall,60)

    # get initial measure of performance
    print( '\nR^2 Scores')
    print( 'glmnet\t\t\t' + str(metrics.r2_score(y_true=testOutput,y_pred=getTestPredictions(testInput, glmnet, True))))
    print( 'ardRegressor\t\t' + str(metrics.r2_score(y_true=testOutput,y_pred=getTestPredictions(testInput, ardRegressor, False))))
    print( 'svrRegressor\t\t' + str(metrics.r2_score(y_true=testOutput,y_pred=getTestPredictions(testInput, svrRegressor, False))))
    print( 'mlp\t\t\t' + str(metrics.r2_score(y_true=testOutput,y_pred=getTestPredictions(testInput, mlpRegressor, False))))
    print ''

    # refit all tools with the full data
    print 'refitting glm...'
    glmnet.fit(tInput, tOutput)
    print 'refitting svr...'
    svrRegressor.fit(tInput, tOutput)
    print 'refitting ard...'
    ardRegressor.fit(tInputSmall[-1500:], tOutputSmall[-1500:])
    print 'refitting mlpRegressor...'
    mlpRegressor.fit(tInput, tOutput)


    # save the input scaler and the model for later use
    print( 'saving scaler and tools...')
    with open("./pickles/scaler.pickle", "wb") as output_file:
        pickle.dump(scaler, output_file)
    with open("./pickles/glmnet.pickle", "wb") as output_file:
        pickle.dump(glmnet, output_file)
    with open("./pickles/svrRegressor.pickle", "wb") as output_file:
        pickle.dump(svrRegressor, output_file)
    with open("./pickles/ardRegressor.pickle", "wb") as output_file:
        pickle.dump(ardRegressor, output_file)
    with open("./pickles/mlpRegressor.pickle", "wb") as output_file:
        pickle.dump(svrRegressor, output_file)

    dbConn.commit()
    dbConn.close()

if __name__ == "__main__":
    main()
