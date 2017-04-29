import subprocess
import os

def getColsAccumulateAndClean(filenames, columns, destination):
    # generate temp filenames, store them, and fill them
    tempnames = []
    for dfile in filenames:
        tempnames.append(dfile+".temp.csv")
        tempfile = open(dfile+".temp.csv", "w")
        command = ["csvcut","-x", "-c"] + [",".join(columns)] + [dfile]
        print "cutting... " + " ".join(command)
        proc = subprocess.call(command, stdout=tempfile )
        tempfile.close()

    # now that columns are pulled, stack the separate files together
    print "stacking..."
    stackedfile = open(destination, "w")
    proc = subprocess.call(["csvstack"] + tempnames, stdout=stackedfile )
    stackedfile.close()

    # remove temporary files
    print "cleaning temporary files..."
    for dfile in tempnames:
        os.remove(dfile)

    # clean the output file
    print "cleaning data..."
    proc = subprocess.call(["csvclean", destination])

    # the REAL destination is really destination_out.csv (out is added by the cleaning process)
    # remove the old destination, and just keep the csvclean one
    os.remove(destination)

# replace invalid bytes with ' '
# ALL SPACES ARE THEN REMOVED FROM THE COLUMN NAMES
def fixFile(filename):
    with open(filename, "rb") as f:
        # find bad bytes
        byte = f.read(1)
        index = 0
        indexlist = []
        while byte != "":
            if byte > '~':
                indexlist.append(index)
            byte = f.read(1)
            index += 1

    # replace the bad bytes
    fh = open(filename, "r+b")
    for i in indexlist:
        fh.seek(i)
        fh.write(' ')
    fh.close()

    # if malformed bytes SOMEHOW HAPPEN TO BE IN THE HEADER OF THE LAST FILE YOU PROCESS
    # go ahead and remove any spaces from the column names
    f = open(filename, "r+")
    line1 = f.readline()
    line2 = line1.replace(" ", "")
    f.close()
    os.rename(filename, filename+".temp")
    f = open(filename+".temp", "r+")
    dest = open(filename, "w+")
    for l in f:
        if l != line1:
            dest.write(l)
        else:
            dest.write(line2)
    f.close()
    dest.close()
    os.remove(filename+".temp")

    if len(indexlist) > 0:
        print "found malformed bytes. These bytes will be replaced by '!' in the data"

def fixFileArr(fileArr):
    for filename in fileArr:
        fixFile(filename)

def addInspectionHeader(filename):
    headerString = "c1,inspection_id,establishment_id,c4,c5,c6,inspection_date,type,c9,c10,c11,c12,score,c14,c15,c16,c17,c18,c19,c20\n"
    source = open(filename, 'r')
    dest = open("./raw_data/adjustedInspectionData.csv", "w+")
    dest.write(headerString)
    for line in source:
        dest.write(line)
    source.close()
    dest.close()

def main():
    # do initial preparation of the 311 data
    fileList311 = ["./raw_data/citizen311data_1.csv", "./raw_data/citizen311data_2.csv", "./raw_data/citizen311data_3.csv", "./raw_data/citizen311data_4.csv", "./raw_data/citizen311data_5.csv", "./raw_data/citizen311data_6.csv", "./raw_data/citizen311data_7.csv"]
    fixFileArr(fileList311)
    cols = ["service_request_id", "description", "service_name", "longitude", "latitude", "requested_datetime"]
    dest = "./clean_data/Citizen311data_7yrs.csv"
    getColsAccumulateAndClean(fileList311, cols, dest)

    # do initial prep of establishment table
    fileListHealthEst = ["./raw_data/Health_Establishments.csv"]
    fixFileArr(fileListHealthEst)
    cols = ["EstablishmentID", "RCodeDesc", "EstType", "PremiseName", "PremiseStreet", "opening_date", "latitude", "longitude"]
    dest = "./clean_data/Establishments.csv"
    getColsAccumulateAndClean(fileListHealthEst, cols, dest)

    # do initial prep of the Inspections Violations table
    fileListHealthInspViolations = ["./raw_data/Health_InspViolations.csv"]
    fixFileArr(fileListHealthInspViolations)
    cols = ["ODATAID","inspection_id","weight","critical_yn"]
    dest = "./clean_data/InspectionViolations.csv"
    getColsAccumulateAndClean(fileListHealthInspViolations, cols, dest)

    #do initial prep for inspection information
    addInspectionHeader("./raw_data/Health_Inspections.csv")
    fileListInspections = ["./raw_data/adjustedInspectionData.csv"]
    fixFileArr(fileListInspections)
    cols = ["inspection_id","establishment_id", "inspection_date", "type" ,"score"]
    dest = "./clean_data/Health_Inspections.csv"
    getColsAccumulateAndClean(fileListInspections, cols, dest)

    #do initial prep for address information
    fileListAddresses = ["./raw_data/Jefferson_County_KY_Address_Points.csv"]
    fixFileArr(fileListAddresses)
    cols = ["FID","HOUSENO", "DIR", "STRNAME", "TYPE", "ZIPCODE", "X","Y"]
    dest = "./clean_data/Address_Points.csv"
    getColsAccumulateAndClean(fileListAddresses, cols, dest)

    #do initial prep for crime information
    fileListCrime = ["./raw_data/Crime_Data_1.csv", "./raw_data/Crime_Data_2.csv", "./raw_data/Crime_Data_3.csv"]
    fixFileArr(fileListCrime)
    cols = ["INCIDENT_NUMBER", "DATE_OCCURED", "BLOCK_ADDRESS", "CITY", "ZIP_CODE"]
    dest = "./clean_data/Crime.csv"
    getColsAccumulateAndClean(fileListCrime, cols, dest)


if __name__ == "__main__":
    main()
