#/bin/bash
# This is the main capture script controler for the HQ camera.

# create log dir
mkdir -p "/home/picoastal/logs/"

# defines where your code is located
workdir="/home/picoastal/picoastal-picam2/src/"
echo "Current work dir is : "$workdir

# get the current date/home/picoastal/
date=$(date)
datestr=$(date +'%Y%m%d_%H%M')
echo "Current date is : "$date

# your configuration file
cfg="/home/picoastal/picoastal-picam2/src/rpi/config_rpi.json"
echo "Capture config file is : "$cfg

# your email configuration
# email="/home/picoastal/.gmail"
# echo "Email config file is : "$email

# change to current work directory
cd $workdir

# current cycle log file
log="/home/picoastal/logs/picoastal_"$datestr".log"
echo "Log file is : "$log

# call the capture script
script=capture.py
echo "Calling script : "$script
python3 $workdir/rpi/$script -cfg $cfg > $log 2>&1
echo $(<$log)

# call the notification
# script=notify.py
# attachemnt=$(tail -n 1 $log)
# echo $attachemnt
# echo "Calling script : "$script
# python3 $workdir$script -cfg $email -log $log -a $attachemnt
