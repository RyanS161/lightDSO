import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from evaluate_rpe import read_trajectory, evaluate_trajectory
import os

# Comparison tools
    # https://github.com/weichnn/Evaluation_Tools
    # https://github.com/gereon-t/trajectopy?tab=readme-ov-file



def clean_GT(results_dir):
    with open(f"{results_dir}/poses.csv", 'r') as gt_file, \
            open(f"{results_dir}/times.txt", 'r') as times_file:
        
        # Read the poses and times
        gt_reader = csv.reader(gt_file)
        next(gt_reader, None) # Skip this line: "# each line is a 3x4 column-major matrix"
        next(gt_reader, None) # Skip this line: "# representing the camera to world transform "
        gt_poses = [list(map(float, row)) for row in gt_reader]

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

def clean_data(results_dir, dso_traj_name):
    with open(f"{results_dir}/{dso_traj_name}.txt", 'r') as dso_file:
        dso_lines = dso_file.readlines()
        dso_poses = [list(map(float, line.split())) for line in dso_lines]
                
        with open(f"{results_dir}/{dso_traj_name}.traj", 'w') as dso_traj_file:
            dso_traj_writer = csv.writer(dso_traj_file)
            # dso_traj_writer.writerow(["time", "tx", "ty", "tz", "qx", "qy", "qz", "qw"])
            for i, dso_line in enumerate(dso_poses):
                dso_traj_writer.writerow(dso_line)
                # print("DSO Pose:", dso_line)



if __name__ == "__main__":
    # if not os.path.isfile(f"{RESULTS_DIR}/gt_traj.traj") or not os.path.isfile(f"{RESULTS_DIR}/{DSO_TRAJ_NAME}.traj"):
    RESULTS_DIR = "/Users/ryanslocum/Downloads/run_data_transfer/"
    PLOT_DIR = "/Users/ryanslocum/Documents/class/seniorThesis/repos/lightDSO/evaluation_tools/plots/"
    result_names = [
        "backwards_2min",
        "close_quarters_2min",
        "completely_planar_2min",
        "frequent_stops_2min",
        "mostly_straight_2min",
        "straight_fullspeed_3min",
        "tricky_2min",
        "turn_around_2min"
    ]

    algo_names = ["dso_result_", "lightDSO_result_a4_"]
    NUM_EVAL = 5

    for name in result_names:
        clean_GT(f"{RESULTS_DIR}{name}")
        for traj_name in algo_names:
            for iter in range(NUM_EVAL):
                print(f"Cleaning data for {name}/{traj_name}{iter}")
                clean_data(f"{RESULTS_DIR}{name}", f"{traj_name}{iter}")


    RPES = {}

    for name in result_names:
        traj_gt = read_trajectory(f"{RESULTS_DIR}{name}/gt_traj.traj")
        for traj_name in algo_names:
            for iter in range(NUM_EVAL):
                traj_est = read_trajectory(f"{RESULTS_DIR}{name}/{traj_name}{iter}.traj")
                try:
                    result = evaluate_trajectory(traj_gt,traj_est,param_max_pairs=0)
                    trans_error = np.array(result)[:,4]
                    rpe = np.mean(trans_error)
                except:
                    rpe = None
                RPES[f"{name}/{traj_name}{iter}"] = rpe
                print(f"Evaluated RPE for {name}/{traj_name}{iter}: {rpe}")




    results_grid = []

    for name in result_names:
        grid = []
        for baseline in [f"{algo_names[0]}{i}" for i in range(NUM_EVAL)]:
            baseline_grid = []
            baseline_rpe = RPES[f"{name}/{baseline}"]

            for modified in [f"{algo_names[1]}{i}" for i in range(NUM_EVAL)]:
            
                modified_rpe = RPES[f"{name}/{modified}"]
                if baseline_rpe is None or modified_rpe is None:
                    percent_improvement = 0
                else:
                    percent_improvement = round(((baseline_rpe - modified_rpe) / baseline_rpe) * 100, 2)

                baseline_grid.append(percent_improvement)
            grid.append(baseline_grid)
        results_grid.append(grid)





    # Convert the results grid to a numpy array
    results_array = np.array(results_grid)

    # Create a directory to save the plots
    os.makedirs(PLOT_DIR + algo_names[1], exist_ok=True)

    # Iterate over each grid
    for i in range(len(result_names)):
        # Create the subplot for the current grid
        fig, ax = plt.subplots(figsize=(10, 10))

        # Create the heatmap for the current grid
        ax.imshow(results_array[i,:,:], cmap='plasma', interpolation='nearest', vmin=-100, vmax=100)

        # Add the numbers to the heatmap
        for x in range(NUM_EVAL):
            for y in range(NUM_EVAL):
                ax.text(y, x, results_array[i, x, y], ha='center', va='center', color='white')

        # Add labels and title to the subplot
        ax.set_xlabel('Modified Trajectory')
        ax.set_ylabel('Baseline Trajectory')
        ax.set_title(f'{result_names[i]}')
        print(f"Average for {result_names[i]}: {np.mean(results_array[i,:,:])}")

        # Save the plot to the plot directory
        plot_path = os.path.join(f'{PLOT_DIR + algo_names[1] + "/"}{i}_{result_names[i]}.png')
        plt.savefig(plot_path)

        # Close the plot
        plt.close(fig)