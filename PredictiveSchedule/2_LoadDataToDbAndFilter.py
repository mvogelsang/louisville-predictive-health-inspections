import subprocess
import os
import sqlite3
import datetime
import sqlQueries
import time

# note, for convenience of writing many separate query functions
# the connection is defined globally
dbConn = sqlite3.connect("./LouData.db", detect_types=sqlite3.PARSE_DECLTYPES);
dbConn.row_factory = sqlite3.Row
dbCursor = dbConn.cursor()
dbCursor.executescript(sqlQueries.E_speedConfigure_0)

def loadData(csvfile):
    subprocess.call(["csvsql", "--db", "sqlite:///./LouData.db", "--insert", "--snifflimit", "1000", csvfile], stdout=open(os.devnull, 'wb'), stderr = open(os.devnull, 'wb'))

def renameTables(renameArr):
    for tup in renameArr:
        dbCursor.execute(sqlQueries.E_tableRename_2
                            .format(current_name=tup[0], target_name=tup[1])
                        )

def removeIrrelevant(tableInformation):
    for table in tableInformation:
        dbCursor.execute(sqlQueries.E_removeIrrelevant_3
                            .format(table_name=table[0], key_name=table[2], view_query=getattr(sqlQueries, table[1]))
        )

def calculateViolations():
    # insert new columns in the inspection table with the correct type
    dbCursor.execute(sqlQueries.E_addColumn_3
                    .format(table_name='Inspections', col_name='criticalViolations', col_type='DECIMAL')
    )
    dbCursor.execute(sqlQueries.E_addColumn_3
                    .format(table_name='Inspections', col_name='noncriticalViolations', col_type='DECIMAL')
    )

    # add the counts for each row
    print 'calculating noncriticalViolations'
    dbCursor.execute(sqlQueries.E_addNoncritical_0)
    print 'calculating criticalViolations'
    dbCursor.execute(sqlQueries.E_addCritical_0)
    dbConn.commit()

def main():
    # load the csv's to the database
    datafiles = os.listdir('./clean_data')
    for df in datafiles:
        print "loading - " + df
        loadData('./clean_data/'+df)

    # give tables more usable names for queries
    print 'data loaded, beginning preprocessing'
    renameTables([('Establishments_out', 'Establishments'), ('InspectionViolations_out', 'Violations'),('Health_Inspections_out', 'Inspections'),('Address_Points_out', 'Addresses'),('Citizen311data_7yrs_out', 'ThreeOneOne'),('Crime_out', 'Crime')])

    # optimize db for speed
    dbCursor.executescript(sqlQueries.E_speedConfigure_0)

    # remove irrelevant rows (as deemed by relevance in the sqlQueries file)
    # although the irrelevant data should be gone, it is best to still
    # use the 'view' queries within each query as data may be added unexpectedly
    # in the future by newly committed code
    removeIrrelevant(sqlQueries.tableInfo)

    # calculate violation totals for each inspection
    calculateViolations()

    # # need to guess the position of crimes since lat/long is not provided
    # guessCrimeLocations()

    # end of run
    print "finishing"
    dbConn.commit()
    dbConn.close()



if __name__ == "__main__":
    main()
