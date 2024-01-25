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
from pysiril.siril   import *
from pysiril.wrapper import *

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

def submitToLiveStack(fitsName,hdr):
    # Create working directories if not exist
    Path(workingFolder).mkdir(parents=True, exist_ok=True)
    Path(workingFolder+"Light").mkdir(parents=True, exist_ok=True)

    # What is the livestack called? If first or we've changed object create a new one
    liveStackName=stackFolder+"{0}-LiveStack.png".format(hdr["OBJECT"])

    # Set up pySiril
    app=Siril()       
    workdir=workingFolder
    app.Execute("set16bits")
    app.Execute("setext fits")
    
    # Has a livestack already been started?
    if (os.path.isfile(liveStackName)):
        # Move the new image into the working folder
        shutil.copy(fitsName, workingFolder+"Light/Main_002.fits")      
        # Stack this image with the current liveStack
        app.Execute("stack Main_ sum -nonorm")
        # Remove working files
        os.system("rm {0}Light/Main_001.fits".format(workingFolder))
        os.system("rm {0}Light/Main_002.fits".format(workingFolder))
        os.system("rm {0}Light/*.seq".format(workingFolder))
        os.system("mv {0}Light/Main_stacked.fits {0}Light/Main_001.fits".format(workingFolder))
        os.system("rm {0}Light/r_Main*.fits".format(workingFolder))
        # Move PNG to web server
        os.system("/usr/bin/convert -flatten {0}Light/Main_stacked.fits {1}".format(workingFolder,liveStackName))
    else:
        # New livestack, put the first image in the working folder
        shutil.copy(fitsName, workingFolder+"Light/Main_001.fits")
        # Move any existing livestacks to a Previous folder
        os.system("mv {0}*.png {0}Previous".format(stackFolder))
        # Create a PNG file of the first image
        print("Converting {0} to {1}\n".format(fitsName,liveStackName))
        os.system("/usr/bin/convert -flatten {0} {1}".format(fitsName,liveStackName))
        
    app.Close()
    del app
    return True

# Variable Declarations
picturesFolder="/home/gtulloch/AstroPictures/"
repoFolder="/home/gtulloch/AstroRepository/"
dbName = "/home/gtulloch/AstroRepository/obsy.db"
stackFolder="/var/www/html/LiveStack/"
workingFolder="/home/gtulloch/SirilWork/"

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
        #if (file_extension !=".fits") or (file_extension !=".fit"):
        #    continue
        print(os.path.join(root, file))
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
            if not (submitToLiveStack(repoFolder+newName,hdr)):
                logging.warning("Warning: File not added to stack is "+newName)
        else:
            logging.warning("File not added to repo - no FRAME card - "+str(os.path.join(root, file)))
            