#!/bin/bash
sudo pip install csvkit
sudo apt install sqlite3
virtualenv ./venv
. ./bin/activate
pip install sklearn
pip install numpy
pip install scipy
pip install pandas
pip install pyglmnet
pip install fpdf
