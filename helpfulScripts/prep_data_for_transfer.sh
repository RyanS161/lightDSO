rm run_data_transfer.zip
rm -r run_data_transfer

cp -r run_data run_data_transfer
rm run_data_transfer/backwards_2min/images.zip
rm run_data_transfer/close_quarters_2min/images.zip
rm run_data_transfer/completely_planar_2min/images.zip
rm run_data_transfer/frequent_stops_2min/images.zip
rm run_data_transfer/mostly_straight_2min/images.zip
rm run_data_transfer/straight_fullspeed_3min/images.zip
rm run_data_transfer/tricky_2min/images.zip
rm run_data_transfer/turn_around_2min/images.zip

zip -r run_data_transfer.zip run_data_transfer
