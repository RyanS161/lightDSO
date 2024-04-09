#!/bin/bash

dir_names=("backwards_2min" "frequent_stops_2min" "tricky_2min" "close_quarters_2min" "mostly_straight_2min" "turn_around_2min" "completely_planar_2min" "straight_fullspeed_3min")
filename_part="lightDSO_result_a4"

for CURRENT_RUN_DIR in "${dir_names[@]}"
do
  for i in {0..4}
  do
    while true; do
      ./bin/dso_dataset  illuminationIntensity=1  illuminationX=0  illuminationY=0  illuminationZ=0 nogui=1 quiet=1 files=~/workspace/run_data/$CURRENT_RUN_DIR/images.zip calib=~/workspace/run_data/$CURRENT_RUN_DIR/camera.txt preset=0 mode=2 resultFile=~/workspace/run_data/$CURRENT_RUN_DIR/${filename_part}_$i.txt
      if [ $? -eq 0 ]; then
        echo "Command finished successfully."
        break
      else
        echo "Command segfaulted, retrying..."
      fi
    done
  done
done
