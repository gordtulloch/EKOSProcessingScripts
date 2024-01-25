#!/bin/bash
HOMEDIR=/home/gtulloch/LiveStack
# How many pictures are in the folder?
NB=$(find $HOMEDIR/Light/*.fits -maxdepth 1 -type f | wc -l)
 
if   [ $NB = "1" ] # First image
then
mv $HOMEDIR/Light/Light_001.fits $HOMEDIR/Light/Main_001.fits >> $HOMEDIR/log.txt
 
elif [ $NB = "2" ]  #s If this is the second image stack it with the current Main image
then
mv $HOMEDIR/Light/Light_001.fits $HOMEDIR/Light/Main_002.fits >> $HOMEDIR/log.txt
siril -s $HOMEDIR/live.ssf -d $HOMEDIR/Light   >> $HOMEDIR/log.txt
rm $HOMEDIR/Light/Main_001.fits >> $HOMEDIR/log.txt
rm $HOMEDIR/Light/Main_002.fits >> $HOMEDIR/log.txt
rm $HOMEDIR/Light/*.seq >> $HOMEDIR/log.txt
mv $HOMEDIR/Light/Main_stacked.fits $HOMEDIR/Light/Main_001.fits >> $HOMEDIR/log.txt
rm $HOMEDIR/Light/r_Main*.fits >> $HOMEDIR/log.txt
rm $HOMEDIR/Light/Main.png >> $HOMEDIR/log.txt
convert -flatten $HOMEDIR/Light/Main_001.fits $HOMEDIR/Light/Main.jpeg >> $HOMEDIR/log.txt
# Copy the result to the web server
cp $HOMEDIR/Light/Main.jpeg /home/var/www/LiveStack/live.jpeg
else
# If we have more than two images we need to do something else
echo "OVERFLOW" >> $HOMEDIR/log.txt
fi
