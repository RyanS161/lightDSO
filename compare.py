import csv, os
import numpy as np
from scipy.spatial.transform import Rotation as R

# Comparison tools
    # https://github.com/weichnn/Evaluation_Tools
    # https://github.com/gereon-t/trajectopy?tab=readme-ov-file


# Get the folder path from the user
RESULTS_DIR = "/Users/ryanslocum/Documents/class/seniorThesis/artifacts/a_very_kind_run"

# Open the three files

def clean_data():
    with open(f"{RESULTS_DIR}/poses.csv", 'r') as gt_file, \
        open(f"{RESULTS_DIR}/dso_result.txt", 'r') as dso_file, \
        open(f"{RESULTS_DIR}/times.txt", 'r') as times_file:

        # Read the poses and times
        gt_reader = csv.reader(gt_file)
        next(gt_reader, None) # Skip this line: "# each line is a 3x4 column-major matrix"
        next(gt_reader, None) # Skip this line: "# representing the camera to world transform "
        gt_poses = [list(map(float, row)) for row in gt_reader]

        dso_lines = dso_file.readlines()
        dso_poses = [list(map(float, line.split())) for line in dso_lines]

        times_reader = csv.reader(times_file, delimiter=' ')
        times = [row[1] for row in times_reader]

        # Convert Spelunk matrices to translation + quaternions
        with open(f"{RESULTS_DIR}/gt_traj.traj", 'w') as gt_traj_file:
            gt_traj_writer = csv.writer(gt_traj_file)
            # gt_traj_writer.writerow(["time", "tx", "ty", "tz", "qx", "qy", "qz", "qw"])
            for i, (gt_line, time) in enumerate(zip(gt_poses, times)):
                print(gt_line)
                gt_rotation_translation_matrix = np.reshape(gt_line, (4, 3)).T

                gt_rotation_matrix = gt_rotation_translation_matrix[:, :3]
                gt_translation = gt_rotation_translation_matrix[:, 3]
                gt_rotation_obj = R.from_matrix(gt_rotation_matrix)


                gt_pose = np.concatenate(([time,], gt_translation, gt_rotation_obj.as_quat()))

                # Write to csv file
                gt_traj_writer.writerow(gt_pose)
                print("GT Pose:", gt_pose)
                
        with open(f"{RESULTS_DIR}/dso_traj.traj", 'w') as dso_traj_file:
            dso_traj_writer = csv.writer(dso_traj_file)
            #C dso_traj_writer.writerow(["time", "tx", "ty", "tz", "qx", "qy", "qz", "qw"])
            for i, dso_line in enumerate(dso_poses):
                dso_traj_writer.writerow(dso_line)
                print("DSO Pose:", dso_line)



if __name__ == "__main__":
    # check if dso_traj.csv and gt_traj.csv exist
    if not os.path.isfile(f"{RESULTS_DIR}/gt_traj.traj") or not os.path.isfile(f"{RESULTS_DIR}/dso_traj.traj"):
        clean_data()
    
    