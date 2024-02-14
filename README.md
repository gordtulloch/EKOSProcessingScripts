# EKOSProcessingScripts
Scripts that can be added to KStars EKOS to perform various processing tasks

**MCP.py**
Master Control Program which oversees all aspects of the observatory

**postProcess.py**
Name files in the Pictures folder according to a standard, load the info into a SQLite database including headers, and move to a repository. 

**liveStack.py**
Adds the image to a live stack to be displayed on a web server.

**fixFitsObject.py**
Fix the OBJECT card on a set of FITS files (it's easy to take images in EKOS that are missing this card)

