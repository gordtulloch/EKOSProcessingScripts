############################################################################################################
#
# Name        : AddToDb.py
# Purpose     : Script to add files to a database from where they are
# Author      : Gord Tulloch
# Date        : February 1 2024
# License     : GPL v3
# Dependencies: Imagemagick and SIRIL needs to be install for live stacking
#               Tested with EKOS, don't know if it'll work with other imaging tools 
# Usage       : This script could be run after an image (single image) or after a sequence if live stacking  
#               is also being run
# TODO:
#      - Calibrate image prior to storing and stacking it (master dark/flat/bias)
#
############################################################################################################ 
import os
from astropy.io import fits
import logging
import sqlite3
import shutil
import uuid
from pathlib import Path
from datetime import datetime

DEBUG=True

# Function definitions
def submitFile(fileName, hdr):
    if "DATE-OBS" in hdr:
        uuidStr=uuid.uuid4()
        sqlStmt="INSERT INTO fitsFile (unid, date, filename) VALUES ('{0}','{1}','{2}')".format(uuidStr,hdr["DATE-OBS"],fileName)
        print(sqlStmt)
        try:
            cur.execute(sqlStmt)
            con.commit()
        except sqlite3.Error as er:
            logging.error('SQLite error: %s' % (' '.join(er.args)))
            logging.error("Exception class is: ", er.__class__)
            logging.error('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.error(traceback.format_exception(exc_type, exc_value, exc_tb))
            
        for card in hdr:
            if type(hdr[card]) not in [bool,int,float]:
                keywordValue=str(hdr[card]).replace('\'',' ')
            else:
                keywordValue = hdr[card]
            sqlStmt="INSERT INTO fitsHeader (thisUNID, parentUNID, keyword, value) VALUES ('{0}','{1}','{2}','{3}')".format(uuid.uuid4(),uuidStr,card,keywordValue)
            print(sqlStmt)
            try:
                cur.execute(sqlStmt)
                con.commit()
            except sqlite3.Error as er:
                logging.error('SQLite error: %s' % (' '.join(er.args)))
                logging.error("Exception class is: ", er.__class__)
                logging.error('SQLite traceback: ')
                exc_type, exc_value, exc_tb = sys.exc_info()
                logging.error(traceback.format_exception(exc_type, exc_value, exc_tb))
    else:
        logging.error("Error: File not added to repo due to missing date is "+fileName)
        return 0
    
    return 1

def createTables():
    if DEBUG:
        cur.execute("DROP TABLE if exists fitsFile")
        cur.execute("DROP TABLE if exists fitsHeader")
    cur.execute("CREATE TABLE if not exists fitsFile(unid, date, filename)")
    cur.execute("CREATE TABLE if not exists fitsHeader(thisUNID, parentUNID, keyword, value)")
    return

# Variable Declarations
sourceFolder="E:/00 Data Repository New/"
repoFolder="E:/00 Data Repository New/"
dbName = repoFolder+"obsy.db"

# Set up Database
con = sqlite3.connect(dbName)
cur = con.cursor()
createTables()

# Set up logging
logging.basicConfig(filename='batchRename.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Scan the pictures folder
for root, dirs, files in os.walk(os.path.abspath(sourceFolder)):
    for file in files:
        file_name, file_extension = os.path.splitext(os.path.join(root, file))
        
        if (file_extension ==".db"):
            print("Processing: ",file_name, file_extension)
            continue
        else:
            print("Processing: ",file_name, file_extension)

        try:
            hdul = fits.open(os.path.join(root, file))
        except ValueError as e:
            logging.warning("Invalid FITS file. File not processed is "+str(os.path.join(root, file)))
            continue   
        hdr = hdul[0].header
        if "FRAME" in hdr:
            print(os.path.join(root, file.replace(" ", "")))
            submitFile(os.path.join(root, file.replace(" ", "")),hdr)
        else:
            logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))
            