# Script to fix object names that were not set properly by EKOS
import os
from astropy.io import fits
import logging

DEBUG=True

# Variable Declarations
picturesFolder="/home/gtulloch/Dropbox/Astronomy/00 Telescope Data/SPAO/20231216/NGC7635"
objectName = "NGC7635"

# Set up logging
logging.basicConfig(filename='fixFitsName.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Scan the pictures folder
for root, dirs, files in os.walk(os.path.abspath(picturesFolder)):
    for file in files:
        file_name, file_extension = os.path.splitext(os.path.join(root, file))
        if file_extension !=".fits":
            continue
        print(os.path.join(root, file))
        hdul = fits.open(os.path.join(root, file))
        hdr = hdul[0].header
        hdr.set('OBJECT', objectName)
        hdul.writeto(os.path.join(root, file),overwrite=True)
