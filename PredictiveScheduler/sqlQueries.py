# all queries should end in '_#' where '#' is arguments they take in total
# this number should be inclusive of the amount needed by nested queries
# query arguments should be globally consistent (an argument name should be used in the same manner everywhere)
# if you are unsure what you are doing, make argument names globally unique

# this is a meta constant relevant to the sql table structure
# it should contain the table name, the row key,
# and the relevant view name for each table
# should have the form '(table, view, key)'
tableInfo = [ ('Establishments','V_relevantEstablishments_0', 'EstablishmentID'), ('Violations','V_relevantViolations_0','ODATAID'), ('Inspections','V_relevantInspections_0','inspection_id'), ('Addresses','V_relevantAddresses_0','FID'), ('ThreeOneOne','V_relevantThreeOneOne_0','service_request_id'), ('Crime','V_relevantCrime_0','INCIDENT_NUMBER') ]

# ----------------------------------  VIEWS  -----------------------------------
# these are subqueries that are meant to be used in other queries
# as such, they all use 'SELECT * FROM...', for compatibility
# as a principle, all non-view queries should specify columns to be selected
# and all view queries should select all columns.
# they should all start with 'V_' in their name
# and their content should be surrounded in parentheses to facilitate usage

V_relevantEstablishments_0 = """
SELECT * FROM Establishments
WHERE EstablishmentID is not null and RCodeDesc is not null
and latitude != 0 and longitude != 0
and RCodeDesc LIKE '%FOOD SERVICE%'
and EstType LIKE 'FOOD SERVICE' and PremiseName not null
and PremiseStreet != 'MOBILE FOOD UNIT'
and opening_date is not null
"""

V_relevantViolations_0 = """
SELECT * from Violations
WHERE inspection_id is not null and weight is not null
and critical_yn is not null
"""

# should double check the type != other line
# THIS ONE IS DEPENDENT ON ESTABLISHMENTS BEING CLEAN
V_relevantInspections_0 = """
SELECT * from Inspections
WHERE inspection_id is not null and establishment_id is not null
and inspection_date is not null and type is not null and score is not null
and type !='FOLLOWUP' and type !='OTHER' and type like '%REGULAR%'
and establishment_id in (select EstablishmentID from Establishments)
"""

V_relevantAddresses_0 = """
SELECT * from Addresses
WHERE HOUSENO is not null and strname is not null and ZIPCODE is not null and x is not null and y is not null
"""

# this one should probably be investigated more
# it is cursory at best, it halfway should mimic
# the kind of 311 complaints that chicago keeps track of
V_relevantThreeOneOne_0 = """
SELECT * from ThreeOneOne
WHERE longitude is not null and latitude is not null and description is not null and requested_datetime is not null and service_name is not null
and ( description like '%GARBAGE%' or description like '%TRASH%' or description like '%JUNK%' or description like '%CART%' or description like '%RATS%' or description like '%FOOD%')
"""

# this one should also be evaluated more as well
V_relevantCrime_0 = """
SELECT * from Crime
WHERE INCIDENT_NUMBER is not null and DATE_OCCURED is not null and BLOCK_ADDRESS is not null and ZIP_CODE is not null
"""

# ---------------------------------  GETTERS  ----------------------------------
# these are non-view queries that only read data from the DB and have no
# permanent effect on it. They should start with 'G_'.

# this data will be processed, and then fed into the analyzer for training
G_modelTrainingInput_0 = "SELECT scoreAverage, criticalViolationAverage, noncriticalViolationAverage, lastScore, lastCriticalCount, lastNoncriticalCount from Models where scoreAverage is not null and criticalViolationAverage is not null and noncriticalViolationAverage is not null and lastScore is not null and lastCriticalCount is not null and lastNoncriticalCount is not null order by inspection_date asc, inspection_id asc"

# this is the corresponding output for the training input
G_modelTrainingOutput_0 = "SELECT resultPowerScore from Models where scoreAverage is not null and criticalViolationAverage is not null and noncriticalViolationAverage is not null and lastScore is not null and lastCriticalCount is not null and lastNoncriticalCount is not null order by inspection_date asc, inspection_id asc"

# used for testing model effectiveness
G_monthOfModels_2 = ("SELECT inspection_id, scoreAverage, criticalViolationAverage, noncriticalViolationAverage, lastScore, lastCriticalCount, lastNoncriticalCount, resultPowerScore from Models " +
    "where inspection_date > date('now', '-{farBound} month') and inspection_date < date('now', '-{closeBound} month')" +
    """and scoreAverage is not null and criticalViolationAverage is not null
    and noncriticalViolationAverage is not null and lastScore is not null
    and lastCriticalCount is not null and lastNoncriticalCount is not null
    order by inspection_date asc""")

# get data to be predicted on for the final output
G_outputDatapoints_0 = ("""
    SELECT establishment_id, scoreAverage, criticalViolationAverage, noncriticalViolationAverage, lastScore, lastCriticalCount, lastNoncriticalCount
    from output
""")

# used to get the start and end of a testing period
G_modelPeriodBounds_1 = """
SELECT min(inspection_date), max(inspection_date) from models
WHERE inspection_id in {rangeIds}
"""

# get ids by predicted score
G_establishmentsByPredictedScore_0 = """
SELECT establishment_id
from output
order by predictedPowerScore asc
"""

G_finalOutput_0 = """
SELECT E.establishmentId as establishment_id, E.PremiseName as Name, E.PremiseStreet as Street, O.predictedPowerScore as PredictedPowerScore, O.priorityRanking as Priority
FROM Establishments as E, Output as O
WHERE E.EstablishmentID = O.establishment_id
ORDER BY O.priorityRanking ASC
"""

G_inspectionAverageForYears_1 = """
SELECT avg(m.resultPowerScore)
FROM models as m
WHERE m.inspection_date > date('now','-{numYrs} years')
"""
# ---------------------------------  EFFECTS  ----------------------------------
# these queries have effects on the db. they should start with 'E_'

# used for renaming the tables to something more sensible
E_tableRename_2 = "ALTER TABLE {current_name} RENAME TO {target_name}"

# used for cleaning out table rows that do not fit into our 'relevant' views
E_removeIrrelevant_3 = "DELETE from {table_name} where {table_name}.{key_name} not in (SELECT temp.{key_name} from ({view_query}) as temp)"

# adds a column to a table
E_addColumn_3 = "ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"

# add critical violation count to the inspection table
E_addCritical_0 = """
UPDATE Inspections
SET criticalViolations =
(
    SELECT Count(*) from (""" + V_relevantViolations_0 + """) as V
    where Inspections.inspection_id=V.inspection_id and V.critical_yn=1
)
"""

# add noncritical violation count to the inspection table
E_addNoncritical_0 = """UPDATE Inspections
SET noncriticalViolations =
(
    SELECT Count(*) from (""" + V_relevantViolations_0 + """) as V
    where Inspections.inspection_id=V.inspection_id and V.critical_yn=0
)
"""

# confiqure db for speed
E_speedConfigure_0 = """
PRAGMA synchronous = OFF;
PRAGMA journal_mode = OFF;
CREATE INDEX IF NOT EXISTS Establishments_EstablishmentID_index ON Establishments(EstablishmentID);
CREATE INDEX IF NOT EXISTS Establishments_opening_date_index ON Establishments(opening_date);
CREATE INDEX IF NOT EXISTS Violations_inspection_id_index ON Violations(inspection_id);
CREATE INDEX IF NOT EXISTS Violations_ODATAID_index ON Violations(ODATAID);
CREATE INDEX IF NOT EXISTS Inspections_inspection_id_index ON Inspections(inspection_id);
CREATE INDEX IF NOT EXISTS Inspections_inspection_date_index ON Inspections(inspection_date);
CREATE INDEX IF NOT EXISTS Inspections_establishment_id_index ON Inspections(establishment_id);
CREATE INDEX IF NOT EXISTS Addresses_ZIPCODE_index ON Addresses(ZIPCODE);
CREATE INDEX IF NOT EXISTS ThreeOneOne_service_request_id_index ON ThreeOneOne(service_request_id);
CREATE INDEX IF NOT EXISTS Crime_INCIDENT_NUMBER_index ON Crime(INCIDENT_NUMBER);

"""

# create table meant to hold model data
E_createModelTable_0 = """
DROP TABLE IF EXISTS models;
CREATE TABLE "Models" (
	inspection_id DECIMAL,
	establishment_id DECIMAL,
	inspection_date TIMESTAMP,
    age DECIMAL,
	scoreAverage DECIMAL,
    powerScoreAverage DECIMAL,
    criticalViolationAverage DECIMAL,
    noncriticalViolationAverage DECIMAL,
    lastScore DECIMAL,
    lastPowerScore DECIMAL,
    lastCriticalCount DECIMAL,
    lastNoncriticalCount DECIMAL,

    resultScore DECIMAL,
    resultPowerScore DECIMAL,
    resultCriticalCount DECIMAL,
    resultNoncriticalCount DECIMAL
);
CREATE INDEX IF NOT EXISTS Models_inspection_id_index ON Models(inspection_id);
CREATE INDEX IF NOT EXISTS Models_establishment_id_index ON Models(establishment_id);
CREATE INDEX IF NOT EXISTS Models_inspection_date_index ON Models(inspection_date)
"""

# create table meant to hold output data
E_createOutputTable_0 = """
DROP TABLE IF EXISTS Output;
CREATE TABLE "Output" (
	establishment_id DECIMAL,
    age DECIMAL,
	scoreAverage DECIMAL,
    powerScoreAverage DECIMAL,
    criticalViolationAverage DECIMAL,
    noncriticalViolationAverage DECIMAL,
    lastScore DECIMAL,
    lastPowerScore DECIMAL,
    lastCriticalCount DECIMAL,
    lastNoncriticalCount DECIMAL,

    resultScore DECIMAL,
    resultPowerScore DECIMAL,
    resultCriticalCount DECIMAL,
    resultNoncriticalCount DECIMAL,

    predictedPowerScore,
    priorityRanking DECIMAL
);
CREATE INDEX IF NOT EXISTS Output_establishment_id_index ON Output(establishment_id);
"""

# fill in basic model table information
E_startModelInfo_0 = """
INSERT INTO Models (inspection_id, establishment_id, inspection_date, resultScore, resultCriticalCount, resultNoncriticalCount)
SELECT i.inspection_id, i.establishment_id, i.inspection_date, i.score, i.criticalViolations, i.noncriticalViolations
from Inspections as i
"""

# fill in unique restaurantIDs from the last 2 years
# that are still in the establishment table
E_fillOutputIds_0 = """
INSERT INTO output (establishment_id)
SELECT DISTINCT i.establishment_id as estid
FROM Inspections AS i
WHERE i.inspection_date > date('now', '-2 years')
AND i.establishment_id in (select EstablishmentID from establishments)

"""

# fill in average information to the model
E_fillInModelAverages_0 = """
UPDATE Models
Set scoreAverage = (select avg(i.score) from (""" + V_relevantInspections_0 + """) as i where i.inspection_date < Models.inspection_date and Models.establishment_id = i.establishment_id),
criticalViolationAverage = (select avg(i.criticalViolations) from (""" + V_relevantInspections_0 + """) as i where i.inspection_date < Models.inspection_date and Models.establishment_id = i.establishment_id),
noncriticalViolationAverage = (select avg(i.noncriticalViolations) from (""" + V_relevantInspections_0 + """) as i where i.inspection_date < Models.inspection_date and Models.establishment_id = i.establishment_id)
"""

# fill in average information to the output
E_fillInOutputAverages_0 = """
UPDATE Output
Set scoreAverage = (select avg(i.score) from Inspections as i where i.inspection_date < date('now') and Output.establishment_id = i.establishment_id),
criticalViolationAverage = (select avg(i.criticalViolations) from Inspections as i where i.inspection_date < date('now') and Output.establishment_id = i.establishment_id),
noncriticalViolationAverage = (select avg(i.noncriticalViolations) from Inspections as i where i.inspection_date < date('now') and Output.establishment_id = i.establishment_id)
"""

# fill in most recent performance values for each model inspection
E_fillInModelRecentValues_0 = """
UPDATE Models
Set lastScore = (select i.score from (""" + V_relevantInspections_0 + """) as i where i.inspection_date < Models.inspection_date and Models.establishment_id = i.establishment_id order by i.inspection_date limit 1),
lastCriticalCount = (select i.criticalViolations from (""" + V_relevantInspections_0 + """) as i where i.inspection_date < Models.inspection_date and Models.establishment_id = i.establishment_id order by i.inspection_date limit 1),
lastNoncriticalCount = (select i.noncriticalViolations from (""" + V_relevantInspections_0 + """) as i where i.inspection_date < Models.inspection_date and Models.establishment_id = i.establishment_id order by i.inspection_date limit 1)
"""

# fill in most recent performance values to the output
E_fillInOutputRecentValues_0 = """
UPDATE Output
Set lastScore = (select i.score from Inspections as i where i.inspection_date < date('now') and Output.establishment_id = i.establishment_id order by i.inspection_date limit 1),
lastCriticalCount = (select i.criticalViolations from Inspections as i where i.inspection_date < date('now') and Output.establishment_id = i.establishment_id order by i.inspection_date limit 1),
lastNoncriticalCount = (select i.noncriticalViolations from Inspections as i where i.inspection_date < date('now') and Output.establishment_id = i.establishment_id order by i.inspection_date limit 1)
"""
# calculate the powerscore heuristics
# this comes from the stipulation that an inspection is a failure when a score of
# below 85 is received, or a critical violation is found
# this essentially means that critical violations are worth at least -16 points
E_calculatePowerScores_0 = """
UPDATE Models
Set powerScoreAverage = (scoreAverage - (16 * criticalViolationAverage)),
lastPowerScore = (lastScore - (16 * lastCriticalCount)),
resultPowerScore = (resultScore - (16 * resultCriticalCount))
"""

E_calculateOutputPowerScores_0 = """
UPDATE Output
Set powerScoreAverage = (scoreAverage - (16 * criticalViolationAverage)),
lastPowerScore = (lastScore - (16 * lastCriticalCount)),
resultPowerScore = (resultScore - (16 * resultCriticalCount))
"""

E_updatePredictedScore_2 = """
UPDATE Output
Set predictedPowerScore = {score_prediction}
Where establishment_id = {est_id}
"""

E_fillInRank_2 = """
UPDATE Output
Set priorityRanking = {ranking}
Where establishment_id = {est_id}
"""
def main():
    for k,v in globals().iteritems():
        print( k)
        print( v)
        print( '\n')

if __name__ == "__main__":
    main()
