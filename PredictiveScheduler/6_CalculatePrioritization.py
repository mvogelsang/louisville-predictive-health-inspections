import subprocess
import os
import sqlite3
import datetime
import sqlQueries
from localUtil import getPrediction, scaler


# note, for convenience of writing many separate query functions
# the connection is defined globally
dbConn = sqlite3.connect("./LouData.db", detect_types=sqlite3.PARSE_DECLTYPES);
dbCursor = dbConn.cursor()
dbCursor.executescript(sqlQueries.E_speedConfigure_0)

def main():
    # create the output table (delete if it already exists and restart)
    print 'creating model table...'
    dbCursor.executescript(sqlQueries.E_createOutputTable_0)
    print'...'
    dbConn.commit()

    # put basic information into the model table
    print 'filling in establishmentIds...'
    dbCursor.execute(sqlQueries.E_fillOutputIds_0)
    print'...'
    dbConn.commit()

    # fill in average information to output
    print 'getting averages...'
    dbCursor.execute(sqlQueries.E_fillInOutputAverages_0)
    print'...'
    dbConn.commit()

    # fill in recent information to output
    print 'getting recent information...'
    dbCursor.execute(sqlQueries.E_fillInOutputRecentValues_0)
    print'...'
    dbConn.commit()

    # fill in the output powerscore statistics
    print 'filling in power scores...'
    dbCursor.execute(sqlQueries.E_calculateOutputPowerScores_0)
    print'...'
    dbConn.commit()

    # grab the datapoints to be predicted on
    # predict their scores, and save back to db
    dbCursor.execute(sqlQueries.G_outputDatapoints_0)
    data = dbCursor.fetchall()
    for datapoint in data:
        dbCursor.execute(sqlQueries.E_updatePredictedScore_2.format(est_id=datapoint[0], score_prediction=getPrediction(scaler.transform(list(datapoint[1:])))))

    # fill in explicit ranking by score
    dbCursor.execute(sqlQueries.G_establishmentsByPredictedScore_0)
    data = dbCursor.fetchall()
    i=0
    while i < len(data):
        establishment_id=data[i][0]
        dbCursor.execute(sqlQueries.E_fillInRank_2.format(est_id=establishment_id, ranking=i+1))
        i += 1

    # end of run
    print "finishing"
    dbConn.commit()
    dbConn.close()


if __name__ == "__main__":
    main()
