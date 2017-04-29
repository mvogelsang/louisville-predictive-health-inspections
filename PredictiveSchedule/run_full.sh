#!/bin/bash
# . ./venv/bin/activate

set -x
cd ./clean_data && rm *.csv
cd ..
rm ./LouData.db
rm ./dbdump.bak
python ./1_CleanData.py
python ./2_LoadDataToDbAndFilter.py
sqlite3 ./LouData.db .dump > dbdump.bak
python ./3_BuildModel.py && sqlite3 ./LouData.db .dump > dbdump.bak
python ./4_TrainModel.py
python ./5_testModelPerformance.py
python ./6_CalculatePrioritization.py
python ./7_ProduceOutput.py
set +x

# deactivate
