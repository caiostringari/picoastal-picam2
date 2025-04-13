#/bin/bash
# This is the main capture script controler

# create log dir
mkdir -p "/home/pi/logs/"  # Change here as needed

# Define where your code is located
workdir="/home/pi/picoastal/src/"
echo "Current work dir is : "$workdir

# Get the current date
date=$(date)
datestr=$(date +'%Y%m%d_%H%M')
echo "Current date is : "$date

# Your configuration file
cfg="/home/pi/picoastal/src/rpi/config_rpi.json"
echo "Capture config file is : "$cfg

# Your email configuration
email="/home/pi/.gmail"
echo "Email config file is : "$email

# Change to current work directory
cd $workdir

# Current cycle log file
log="/home/pi/logs/picoastal_"$datestr".log"
echo "Log file is : "$log

# Call the capture script
script=capture.py
echo "Calling script : "$script
python3 $workdir/rpi/$script -cfg $cfg > $log 2>&1
echo $(<$log)

# Optional Post-processing

# statistical images
capdate=$(date +'%Y%m%d_%H%00')
python3 $workdir/post/average.py -i "/mnt/data/$capdate/" -o "average_$datestr.png"
python3 $workdir/post/variance.py -i "/mnt/data/$capdate/" -o "variance_$datestr.png"
python3 $workdir/post/brightest_and_darkest.py -i "/mnt/data/$capdate/" -b "brightest_$datestr.png" -d "darkest_$datestr.png"

# rectified images
python3 $workdir/post/rectify.py -i "average_$datestr.png" -o "average_rect_$datestr.tif" -gcps "xyzuv.csv" --camera_matrix "camera_matrix.json" --epsg "12345" --bbox "xmin,ymin,dx,dy"
python3 $workdir/post/rectify.py -i "variance_$datestr.png" -o "variance_$datestr.png" -gcps "xyzuv.csv" --camera_matrix "camera_matrix.json" --epsg "12345" --bbox "xmin,ymin,dx,dy"
python3 $workdir/post/rectify.py -i "brightest_$datestr.png" -o "brightest_rect_$datestr.tif" -gcps "xyzuv.csv" --camera_matrix "camera_matrix.json" --epsg "12345" --bbox "xmin,ymin,dx,dy"
python3 $workdir/post/rectify.py -i "brightest_$datestr.png" -o "brightest_rect_$datestr.png" -gcps "xyzuv.csv" --camera_matrix "camera_matrix.json" --epsg "12345" --bbox "xmin,ymin,dx,dy"

# timestack
python3 src/post/timestack.py -i "/mnt/data/$capdate/" -o "timestack_$datestr.nc" -gcps "xyzuv.csv" --camera_matrix "camera_matrix.json" --stackline "x1,y1,x2,y2"

# Call the notification
script=notify.py
attachment=$(tail -n 1 $log)
echo $attachment
echo "Calling script : "$script
python3 $workdir$script -cfg $email -log $log -a $attachment