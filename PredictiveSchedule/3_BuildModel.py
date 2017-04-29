import subprocess
import os
import sqlite3
import datetime
import sqlQueries

# note the city of Louisville has a bounding box roughly described as
# -85.9363274129697 to -85.405993517431 on longitude
# 38.0024567750505 to 38.3772197252928 on latitude
# note, that while longitude is 'x' and latitude is 'y'
# coordinates are written as latitude, longitude
# the diagonals of this box are about 38.75 miles apart
# moving .01 in longitude constitutes moving roughly .54 mile in Louisville (.00926 for half mile)
# moving .01 in latitude is roughly .69 miles (.00725 for half mile)


# note, for convenience of writing many separate query functions
# the connection is defined globally
dbConn = sqlite3.connect("./LouData.db", detect_types=sqlite3.PARSE_DECLTYPES);
dbConn.row_factory = sqlite3.Row
dbCursor = dbConn.cursor()
dbCursor.executescript(sqlQueries.E_speedConfigure_0)

def main():
    # create the model table (delete if it already exists and restart)
    print 'creating model table...'
    dbCursor.executescript(sqlQueries.E_createModelTable_0)
    print'...'
    dbConn.commit()

    # put basic information into the model table
    print 'filling in basic model information...'
    dbCursor.execute(sqlQueries.E_startModelInfo_0)
    print'...'
    dbConn.commit()

    # fill in average information to model
    print 'getting averages...'
    dbCursor.execute(sqlQueries.E_fillInModelAverages_0)
    print'...'
    dbConn.commit()

    # fill in recent information to model
    print 'getting recent information...'
    dbCursor.execute(sqlQueries.E_fillInModelRecentValues_0)
    print'...'
    dbConn.commit()


    # fill in the (potentially useful) model powerscore statistics
    print 'filling in power scores...'
    dbCursor.execute(sqlQueries.E_calculatePowerScores_0)
    print'...'
    dbConn.commit()

    # need to fill in crime and 311 still

    # end of run
    print "finishing"
    dbConn.commit()
    dbConn.close()


if __name__ == "__main__":
    main()
