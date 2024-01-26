############################################################################################################
#
# Name        : postProcess.py
# Purpose     : Script to call after an image is taken to give it a standard name, add it to an index 
#               database, and move it to a repository
# Author      : Gord Tulloch
# Date        : January 25 2024
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

DEBUG=True

# Function definitions
def submitFile(fileName, hdr):
    if "DATE-OBS" in hdr:
        uuidStr=uuid.uuid4()
        sqlStmt="INSERT INTO fitsFile (unid, date, filename) VALUES ('{0}','{1}','{2}')".format(uuidStr,hdr["DATE-OBS"],fileName)

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
picturesFolder="/home/gtulloch/AstroPictures/"
repoFolder="/home/gtulloch/AstroRepository/"
dbName = "/home/gtulloch/AstroRepository/obsy.db"

# Set up Database
con = sqlite3.connect(dbName)
cur = con.cursor()
createTables()

# Set up logging
logging.basicConfig(filename='postProcess.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Scan the pictures folder
for root, dirs, files in os.walk(os.path.abspath(picturesFolder)):
    for file in files:
        file_name, file_extension = os.path.splitext(os.path.join(root, file))
        # Ignore everything not a *fit* file
        if (file_extension !=".fits") or (file_extension !=".fit"):
            continue
        
        hdul = fits.open(os.path.join(root, file))
        hdr = hdul[0].header
        if "FRAME" in hdr:
            print(os.path.join(root, file))
            if (hdr["FRAME"]=="Light"):
                if ("OBJECT" in hdr):
                    newName="{0}-{1}-{2}-e{3}s-b{4}x{5}-t{6}.fits".format(hdr["DATE-OBS"],hdr["OBJECT"],hdr["FILTER"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
                else:
                    logging.warning("Invalid object name in header. File not processed is "+str(os.path.join(root, file)))
                    continue
            elif hdr["FRAME"]=="Dark":
                newName="{0}-{1}-{2}s-{3}x{4}-t{5}".format(hdr["DATE-OBS"],hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])              
            elif hdr["FRAME"]=="Flat":
                newName="{0}-{1}-{2}s-{3}x{4}-t{5}".format(hdr["DATE-OBS"],hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
            elif hdr["FRAME"]=="Bias":
                newName="{0}-{1}-{2}s-{3}x{4}-t{5}".format(hdr["DATE-OBS"],hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["CCD-TEMP"])
            else:
                logging.warning("File not processed as FRAME not recognized: "+str(os.path.join(root, file)))
                
            # If we can add the file to the database move it to the repo
            if (submitFile(repoFolder+newName.replace(" ", ""),hdr)):
                shutil.move(os.path.join(root, file),repoFolder+newName)
                moveInfo="Moving {0} to {1}\n".format(os.path.join(root, file),repoFolder+newName)
            else:
                logging.warning("Warning: File not added to repo is "+str(os.path.join(root, file)))
        else:
            logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))
            