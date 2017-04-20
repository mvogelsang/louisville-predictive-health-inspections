import csv
import json

#opens the complaint log file make sure to it is in the same folder as this program
with open('ComplaintLog.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

#creates the output file currently test.json
with open('test.json', 'w') as f:
    json.dump ({"Tweets": rows}, f)
    
