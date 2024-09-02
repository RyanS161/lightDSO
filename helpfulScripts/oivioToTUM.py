import os
import zipfile
import shutil
import yaml
import numpy as np


SRC_DIR = '/Users/ryanslocum/Documents/CU/class/seniorThesis/OIVIO_data/unzipped'

# Iterate through all folders in the directory
for folder in os.listdir(SRC_DIR):
    parent_path = os.path.join(SRC_DIR, folder)
    if os.path.isdir(parent_path):
        # Your code here to process each directory
        # ...

        # If there's a husky0 file, go one deeper
        if os.path.exists(parent_path + '/husky0'):
            working_path = parent_path + '/husky0'
        else:
            working_path = parent_path
        print(working_path)


        cam0_transform = None
        # process cam0 file
            # zip all images in camo0/data into images.zip
        if os.path.exists(working_path + '/cam0'):
            cam0_path = os.path.join(working_path, 'cam0')
            image_files = [file for file in os.listdir(os.path.join(cam0_path, 'data')) if file.endswith('.png')]
            with zipfile.ZipFile(os.path.join(parent_path, 'images.zip'), 'w') as zipf:
                for file in image_files:
                    zipf.write(os.path.join(cam0_path, 'data', file), file)
            # copy vignette.png to vignette.png
            vignette_path = os.path.join(working_path, 'cam0', 'vignette.png')
            if os.path.exists(vignette_path):
                shutil.copy(vignette_path, parent_path)
            else:
                print('No vignette.png file found in ' + cam0_path)
            # copy response.txt to pcalib.txt
            response_path = os.path.join(working_path, 'cam0', 'response.txt')
            if os.path.exists(response_path):
                shutil.copy(response_path, os.path.join(parent_path, 'pcalib.txt'))
            else:
                print('No response.txt file found in ' + cam0_path)
            # process data.csv into times.txt
            data_path = os.path.join(working_path, 'cam0', 'data.csv')
            if os.path.exists(data_path):
                with open(data_path, 'r') as data_file:
                    lines = data_file.readlines()
                    # Ignore header line
                    lines = lines[1:]
                    # Extract column0 values
                    time_values = [int(line.split(',')[0]) for line in lines]
                    exposure_values = [int(line.split(',')[1]) for line in lines]
                    # Write to times.txt
                    times_path = os.path.join(parent_path, 'times.txt')
                    with open(times_path, 'w') as times_file:
                        for time, exposure in zip(time_values, exposure_values):
                            times_file.write(f"{time} {time*10e-9} 0.0\n")
            else:
                print('No data.csv file found in ' + cam0_path)
            # process sensor.yaml into camera.txt
            sensor_path = os.path.join(working_path, 'cam0', 'sensor.yaml')
            if os.path.exists(sensor_path):
                with open(sensor_path, 'r') as file:
                    sensor_data = yaml.safe_load(file)

                    # Extract the required data
                    distortion_model = sensor_data['distortion_model']
                    if distortion_model != 'radial-tangential':
                        print('Distortion model is not radtan')
                        break
                    intrinsics = sensor_data['intrinsics']
                    resolution = sensor_data['resolution']
                    distortion_coefficients = sensor_data['distortion_coefficients']
                    cam0_transform = np.array(sensor_data['T_BS']['data']).reshape(4, 4)

                    # Prepare the data for the camera.txt file
                    camera_data = f"RadTan {intrinsics[0]} {intrinsics[1]} {intrinsics[2]} {intrinsics[3]} {distortion_coefficients[0]} {distortion_coefficients[1]} {distortion_coefficients[2]} {distortion_coefficients[3]}\n"
                    camera_data += f"{resolution[0]} {resolution[1]}\n"
                    camera_data += f"crop\n"
                    camera_data += f"{resolution[0]} {resolution[1]}"


                    # Write the data to the camera.txt file
                    camera_data_path = os.path.join(parent_path, 'camera.txt')
                    with open(camera_data_path, 'w') as file:
                        file.write(camera_data)
            else:
                print('No sensor.yaml file found in ' + cam0_path)
        # process leica0 file
        if os.path.exists(working_path + '/leica0'):
            leica0_path = os.path.join(working_path, 'leica0')
            if os.path.exists(os.path.join(leica0_path, 'data.csv')):
                with open(os.path.join(leica0_path, 'data.csv'), 'r') as data_file:
                    lines = data_file.readlines()
                    # Ignore header line
                    lines = lines[1:]
                    # Write to poses.txt
                    gt_path = os.path.join(parent_path, 'leica0_gt.txt')
                    with open(gt_path, 'w') as gt_file:
                        for line in lines:
                            time = int(line.split(',')[0])*10e-9
                            pose_str = line.split(',')[1:]
                            pose_str = ' '.join(pose_str)
                            gt_file.write(f"{time} {pose_str} 0 0 0 0")
        # process loop0 file
        if os.path.exists(working_path + '/loop0'):
            #### TODO: figure out how to incorporate transform
            loop0_path = os.path.join(working_path, 'loop0')
            if os.path.exists(os.path.join(loop0_path, 'data.csv')):
                with open(os.path.join(loop0_path, 'data.csv'), 'r') as data_file:
                    lines = data_file.readlines()
                    # Ignore header line
                    lines = lines[1:]
                    # Write to times.txt
                    gt_path = os.path.join(parent_path, 'loop0_gt.txt')
                    with open(gt_path, 'w') as gt_file:
                        for line in lines:
                            time = int(line.split(',')[0])*10e-9
                            pose_str = line.split(',')[1:]
                            pose_str = ' '.join(pose_str)
                            gt_file.write(f"{time} {pose_str}")

        # Delete all folders in the parent folder
        for folder in os.listdir(parent_path):
            folder_path = os.path.join(parent_path, folder)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)