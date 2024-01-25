# EKOSProcessingScripts
Scripts that can be added to KStars EKOS to perform various processing tasks

**postProcess.py**
Name files in the Pictures folder according to a standard, load the info into a SQLite database including headers, and move to a repository. Also adds the image to a live stack.

**fixFitsObject.py**
Fix the OBJECT card on a set of FITS files (it's easy to take images in EKOS that are missing this card)

**ekosSchedulerRun.py**
Simple script to run an EKOS Schedule from the local workstation (not my code)

**runEKOS.py**
Control EKOS from the command line. (Not my code)
