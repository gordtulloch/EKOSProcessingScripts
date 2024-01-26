############################################################################################################
#
# Name        : liveStack.py
# Purpose     : Script to detect images being added to a repository real time and stack them to a web server
# Author      : Gord Tulloch
# Date        : January 25 2024
# License     : GPL v3
# Dependencies: Imagemagick and SIRIL needs to be install for live stacking
#               Tested with EKOS, don't know if it'll work with other imaging tools 
# TODO:
#      - Calibrate image prior to storing and stacking it (master dark/flat/bias)
#
############################################################################################################ 
from pysiril.siril   import *
from pysiril.wrapper import *

# Variable definitions
picturesFolder="/home/gtulloch/Pictures/"
workingFolder="/home/gtulloch/SirilWork/"

# Create working directories if not exist
Path(workingFolder).mkdir(parents=True, exist_ok=True)
Path(workingFolder+"Light").mkdir(parents=True, exist_ok=True)

# What is the livestack called? If first or we've changed object create a new one
liveStackName=stackFolder+"{0}-LiveStack.png".format(hdr["OBJECT"])

# Set up pySiril
app=Siril()
cmd=Wrapper(app)
cmd.set16bits()
cmd.setext('fits')

# Detect any new files in the images folder

# Has a livestack already been started?
if (os.path.isfile(liveStackName)):
    # Move the new image into the working folder
    shutil.copy(fitsName, workingFolder+"Light/Main_002.fits")      
    # Stack this image with the current liveStack
    try:
        cmd.cd(workingFolder+"/Light")
        cmd.stack("Main_",type='sum',output_norm=False)
    except Exception as e :
    print("\n**** ERROR *** " +  str(e) + "\n" )  
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
