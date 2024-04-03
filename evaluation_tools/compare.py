import csv
import numpy as np
from scipy.spatial.transform import Rotation as R
from evaluate_rpe import read_trajectory, evaluate_trajectory

# Comparison tools
    # https://github.com/weichnn/Evaluation_Tools
    # https://github.com/gereon-t/trajectopy?tab=readme-ov-file



def clean_data(results_dir, dso_traj_name):
    with open(f"{results_dir}/poses.csv", 'r') as gt_file, \
        open(f"{results_dir}/{dso_traj_name}.txt", 'r') as dso_file, \
        open(f"{results_dir}/times.txt", 'r') as times_file:

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
        with open(f"{results_dir}/gt_traj.traj", 'w') as gt_traj_file:
            gt_traj_writer = csv.writer(gt_traj_file)
            # gt_traj_writer.writerow(["time", "tx", "ty", "tz", "qx", "qy", "qz", "qw"])
            for i, (gt_line, time) in enumerate(zip(gt_poses, times)):
                # print(gt_line)
                gt_rotation_translation_matrix = np.reshape(gt_line, (4, 3)).T

                gt_rotation_matrix = gt_rotation_translation_matrix[:, :3]
                gt_translation = gt_rotation_translation_matrix[:, 3]
                gt_rotation_obj = R.from_matrix(gt_rotation_matrix)


                gt_pose = np.concatenate(([time,], gt_translation, gt_rotation_obj.as_quat()))

                # Write to csv file
                gt_traj_writer.writerow(gt_pose)
                # print("GT Pose:", gt_pose)
                
        with open(f"{results_dir}/{dso_traj_name}.traj", 'w') as dso_traj_file:
            dso_traj_writer = csv.writer(dso_traj_file)
            #C dso_traj_writer.writerow(["time", "tx", "ty", "tz", "qx", "qy", "qz", "qw"])
            for i, dso_line in enumerate(dso_poses):
                dso_traj_writer.writerow(dso_line)
                # print("DSO Pose:", dso_line)



if __name__ == "__main__":
    # if not os.path.isfile(f"{RESULTS_DIR}/gt_traj.traj") or not os.path.isfile(f"{RESULTS_DIR}/{DSO_TRAJ_NAME}.traj"):
    RESULTS_DIR = "/Users/ryanslocum/Downloads/run_data/"
    result_names = [
        "backwards_2min",
        "close_quarters_2min",
        "completely_planar_2min",
        # "completely_stationary_1min",
        "frequent_stops_2min",
        "mostly_straight_2min",
        "only_rotation_2min",
        "straight_fullspeed_3min",
        "tricky_2min",
        "turn_around_2min"
    ]
    for name in result_names:
        for traj_name in ["dso_baseline_result", "dso_attempt1_result"]:
            clean_data(f"{RESULTS_DIR}{name}", traj_name)



    total = 0

    for name in result_names:
        rpes = []
        traj_gt = read_trajectory(f"{RESULTS_DIR}{name}/gt_traj.traj")
        for traj_name in ["dso_baseline_result", "dso_attempt1_result"]:
            traj_est = read_trajectory(f"{RESULTS_DIR}{name}/{traj_name}.traj")
            result = evaluate_trajectory(traj_gt,traj_est,param_max_pairs=0)
            trans_error = np.array(result)[:,4]
            # print(f"{name}/{traj_name} RPE: {np.mean(trans_error)}")
            rpes.append(np.mean(trans_error))


        percent_improvement = round(((rpes[0] - rpes[1]) / rpes[0] )* 100 ,2)
        total += percent_improvement
        print(f"{name}/{traj_name} RPE percent improvement: {percent_improvement}%")
        print()

    print(f"Avg percent improvement: {round(total/len(result_names), 2)}%")