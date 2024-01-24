# Script to call after single image to calibrate and name it properly
import os
from astropy.io import fits
import logging
import sqlite3
import shutil
import uuid

DEBUG=True

# Function definitions
def submitFile(fileName, hdr):
    if "DATE-OBS" in hdr:
        uuidStr=uuid.uuid4()
        sqlStmt="INSERT INTO fitsFile (unid, date, filename) VALUES ('{0}','{1}','{2}')".format(uuidStr,hdr["DATE-OBS"],fileName)
        if DEBUG:
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
            print(type(hdr[card]))
            if type(hdr[card]) not in [bool,int,float]:
                keywordValue=str(hdr[card]).replace('\'',' ')
            else:
                keywordValue = hdr[card]
            sqlStmt="INSERT INTO fitsHeader (thisUNID, parentUNID, keyword, value) VALUES ('{0}','{1}','{2}','{3}')".format(uuid.uuid4(),uuidStr,card,keywordValue)
            if DEBUG:
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
picturesFolder="/home/gtulloch/Dropbox/Astronomy/00 Telescope Data/SPAO/"
repoFolder="/home/gtulloch/Dropbox/Astronomy/00 Data Repository/"
dbName = "/home/gtulloch/Dropbox/Astronomy/00 Data Repository/obsy.db"

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
        if file_extension !=".fits":
            continue
        #print(os.path.join(root, file))
        hdul = fits.open(os.path.join(root, file))
        hdr = hdul[0].header
        if "FRAME" in hdr:
            #print(os.path.join(root, file))
            if (hdr["FRAME"]=="Light"):
                if ("OBJECT" in hdr):
                    newName="{0}-{1}-{2}-e{3}s-b{4}x{5}-g{6}-o{7}-t{8}.fits".format(hdr["DATE-OBS"],hdr["OBJECT"],hdr["FILTER"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["GAIN"],hdr["OFFSET"],hdr["CCD-TEMP"])
                else:
                    logging.warning("Warning: Invalid object name in header. File not processed is "+str(os.path.join(root, file)))
                    continue
            elif hdr["FRAME"]=="Dark":
                newName="{0}-{1}-{2}s-{3}x{4}-g{5}-o{6}-t{7}".format(hdr["DATE-OBS"],hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["GAIN"],hdr["OFFSET"],hdr["CCD-TEMP"])              
            elif hdr["FRAME"]=="Flat":
                newName="{0}-{1}-{2}s-{3}x{4}-g{5}-o{6}-t{7}".format(hdr["DATE-OBS"],hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["GAIN"],hdr["OFFSET"],hdr["CCD-TEMP"])
            elif hdr["FRAME"]=="Bias":
                newName="{0}-{1}-{2}s-{3}x{4}-g{5}-o{6}-t{7}".format(hdr["DATE-OBS"],hdr["FRAME"],hdr["EXPTIME"],hdr["XBINNING"],hdr["YBINNING"],hdr["GAIN"],hdr["OFFSET"],hdr["CCD-TEMP"])
            # If we can add the file to the database move it to the repo
            if (submitFile(repoFolder+newName.replace(" ", ""),hdr)):
                shutil.move(os.path.join(root, file),repoFolder+newName)
                moveInfo="Moving {0} to {1}\n".format(os.path.join(root, file),repoFolder+newName)
                if DEBUG:
                    print(moveInfo)
            else:
                logging.warning("Warning: File not added to repo is "+str(os.path.join(root, file)))
                        