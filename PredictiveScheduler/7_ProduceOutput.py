import subprocess
import os
import sqlite3
import datetime
import sqlQueries
from localUtil import getPrediction, scaler
import json
import csv

# note, for convenience of writing many separate query functions
# the connection is defined globally
dbConn = sqlite3.connect("./LouData.db", detect_types=sqlite3.PARSE_DECLTYPES);
dbConn.row_factory = sqlite3.Row
dbCursor = dbConn.cursor()
dbCursor.executescript(sqlQueries.E_speedConfigure_0)


def main():
    # get final output data
    dbCursor.execute(sqlQueries.G_finalOutput_0)
    data = dbCursor.fetchall()

    # initialize containers that will get saved as JSON
    minJSON = []
    verboseJSON = []

    print 'building output...'
    # fill the containers
    for datapoint in data:
        appender = {}
        appender["Establishment_ID"]   = datapoint['establishment_id']
        appender["Establishment_Rank"] = datapoint['Priority']
        appender["Establishment_Name"] = datapoint['Name']

        minJSON.append(appender)
        appender=appender.copy() #dicts are references, so need a new reference

        appender['Establishment_Street'] = datapoint['Street']
        appender['Establishment_PredictedPowerScore'] = datapoint['predictedPowerScore']

        verboseJSON.append(appender)

    print 'saving output...'
    # wrap the min json array in a Dict for use by the site
    minJSONShell = {'Establishments': minJSON}

    # save minJSON to file
    # note minjson is a dict that wraps and array of dicts
    with open('./output/output.json', 'w') as outfile:
        json.dump(minJSONShell, outfile)

    # save verboseJSON to file
    # note verbose is just an array of dicts
    with open('./output/verboseOutput.json', 'w') as outfile:
        json.dump(verboseJSON, outfile)

    # for convenience, also output the verbose results to a csv
    keys = verboseJSON[0].keys()
    with open('./output/verboseOutput.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(verboseJSON)


    # end of run
    print "finishing"
    dbConn.commit()
    dbConn.close()


if __name__ == "__main__":
    main()
