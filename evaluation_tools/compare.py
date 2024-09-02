import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from evaluate_rpe import read_trajectory, evaluate_trajectory
from evaluate_ate import evaluate_ate
import os
from tqdm import tqdm
import json

ALGO_NAMES = ["dso_result_", "lightDSO_result_ill1_"]

RESULTS_DIR = "/Users/ryanslocum/Downloads/artifacts/run_data_transfer/"
PLOT_DIR = "/Users/ryanslocum/Documents/class/seniorThesis/repos/lightDSO/evaluation_tools/plots/" + ALGO_NAMES[1]
SIM_RESULT_NAMES = [
    "backwards_2min",
    "close_quarters_2min",
    "completely_planar_2min",
    "frequent_stops_2min",
    "mostly_straight_2min",
    "straight_fullspeed_3min",
    "tricky_2min",
    "turn_around_2min"
]
OIVIO_RESULT_NAMES = [
    "LB_015_HH_01",
    "LB_015_HH_02",
    "LB_015_HH_03",
    "LB_050_HH_01",
    "LB_050_HH_02",
    "LB_050_HH_03",
    "LB_100_HH_01",
    "LB_100_HH_02",
    "LB_100_HH_03",
    "MN_015_HH_01",
    "MN_050_HH_01",
    "MN_100_HH_01",
    "TN_015_HH_01",
    "TN_015_HH_02",
    "TN_015_HH_03",
    "TN_050_HH_01",
    "TN_050_HH_02",
    "TN_050_HH_03",
    "TN_100_HH_01",
    "TN_100_HH_02",
    "TN_100_HH_03",
]

RESULT_NAMES = SIM_RESULT_NAMES

NUM_EVAL = 50
ITER = [f"{n:02d}" for n in range(NUM_EVAL)]

def clean_sim_GT(results_dir):
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

                # gt_rotation_matrix = gt_rotation_translation_matrix[:, :3]
                # gt_translation = gt_rotation_translation_matrix[:, 3]
                # gt_rotation_obj = R.from_matrix(gt_rotation_matrix)


                # Your original matrices
                gt_rotation_matrix = gt_rotation_translation_matrix[:, :3]
                gt_translation = gt_rotation_translation_matrix[:, 3]
                gt_rotation_obj = R.from_matrix(gt_rotation_matrix)


                rotation_matrix_90_x = np.array([[1, 0, 0],
                                                 [0, 0, -1],
                                                 [0, 1, 0]]) 
                rotation_matrix_neg90_x = np.array([[1, 0, 0],
                                                    [0, 0, 1],
                                                    [0, -1, 0]])
                    
                rotation_matrix_90_y = np.array([[0, 0, 1],
                                                 [0, 1, 0],
                                                 [-1, 0, 0]]) 
                rotation_matrix_neg90_y = np.array([[0, 0, -1],
                                                 [0, 1, 0],
                                                 [1, 0, 0]]) 
                
                rotation_matrix_90_z = np.array([[0, -1, 0],
                                                 [1, 0, 0],
                                                 [0, 0, 1]]) 
                rotation_matrix_neg90_z = np.array([[0, 1, 0],
                                                 [-1, 0, 0],
                                                 [0, 0, 1]]) 
                
                rotation_matrix_eye = np.eye(3)
                


                # Create rotation objects from the matrices
                # rotation_obj_y = R.from_matrix(rotation_matrix_y)
                # rotation_obj_z = R.from_matrix(rotation_matrix_z)
                # correction_rotation_obj = rotation_obj_y * rotation_obj_z
                correction_rotation_obj = R.from_matrix(rotation_matrix_eye)

                result_rotation_obj = gt_rotation_obj * correction_rotation_obj

                # Get the resulting rotation matrix
                gt_translation = np.append(gt_translation, [1])  # Convert to homogeneous coordinates
                correction_homogenous = np.vstack((np.hstack((correction_rotation_obj.as_matrix(), np.zeros((3,1)))), np.array([0, 0, 0, 1])))
                # print(correction_homogenous)
                gt_translation_rotated = correction_homogenous @ gt_translation  # Apply rotation
                gt_translation_rotated = gt_translation_rotated[:3]  # Conv

                gt_pose = np.concatenate(([time,], gt_translation_rotated, result_rotation_obj.as_quat()))
                # Write to csv file
                gt_traj_writer.writerow(gt_pose)
                # print("GT Pose:", gt_pose)

def clean_OIVIO_GT(results_dir):
    # check if the ground truth file is leica0.txt or loop0.txt
    if os.path.exists(f"{results_dir}/leica0_gt.txt"):
        gt_method = "leica0_gt"
    elif os.path.exists(f"{results_dir}/loop0_gt.txt"):
        gt_method = "loop0_gt"
    else:
        print("Error: No ground truth file found")
        return
    with open(f"{results_dir}/{gt_method}.txt", 'r') as dso_file:
        dso_lines = dso_file.readlines()
        dso_poses = [list(map(float, line.split())) for line in dso_lines]
                
        with open(f"{results_dir}/gt_traj.traj", 'w') as dso_traj_file:
            dso_traj_writer = csv.writer(dso_traj_file)
            # dso_traj_writer.writerow(["time", "tx", "ty", "tz", "qx", "qy", "qz", "qw"])
            for i, dso_line in enumerate(dso_poses):
                dso_traj_writer.writerow(dso_line)
                # print("DSO Pose:", dso_line)

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



def read_traj_xyz(filename):
    x,y,z = [],[],[]
    with open(filename, 'r') as gt_file:
        gt_reader = csv.reader(gt_file)
        gt_poses = [list(map(float, row)) for row in gt_reader]

        x = [pose[1] for pose in gt_poses]
        y = [pose[2] for pose in gt_poses]
        z = [pose[3] for pose in gt_poses]

    return x, y, z


def top_down_plots():
    for name in RESULT_NAMES:
            plot = plt.figure()
            plt.xlabel('X')
            plt.ylabel('Z')
            plt.title(f'Trajectories for {name}')
            xyz = read_traj_xyz(f"{RESULTS_DIR}{name}/gt_traj.traj")
            plt.plot(xyz[0], xyz[2], label='Ground Truth', color='black')
            for traj_name in ALGO_NAMES:
                color = 'green' if traj_name == "dso_result_" else 'red'
                linestyle = '--' if traj_name == "dso_result_" else '-'
                label = 'DSO' if traj_name == "dso_result_" else 'modified DSO'

                for iter in ITER:
                    xyz = read_traj_xyz(f"{RESULTS_DIR}{name}/{traj_name}{iter}.traj")
                    plt.plot(xyz[0], xyz[2], label=label, color=color, linestyle=linestyle)

            handles, labels = plt.gca().get_legend_handles_labels()
            # labels will be the keys of the dict, handles will be values
            temp = {k:v for k,v in zip(labels, handles)}
            plt.legend(temp.values(), temp.keys(), loc='best')

            plt.savefig(f'{PLOT_DIR + "/"}trajOverlay_{name}.png')
            plt.close(plot)

def three_d_plots():
    for name in RESULT_NAMES:
            xyz = read_traj_xyz(f"{RESULTS_DIR}{name}/gt_traj.traj")
            plt.title('3D Trajectory')
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.set_xlabel('X Label')
            ax.set_ylabel('Y Label')
            ax.set_zlabel('Z Label')

            plt.plot(xyz[0], xyz[1], xyz[2], label='Ground Truth', color='black')

            for traj_name in ALGO_NAMES:
                color = 'green' if traj_name == "dso_result_" else 'red'
                linestyle = '--' if traj_name == "dso_result_" else '-'

                for iter in ITER:
                    xyz = read_traj_xyz(f"{RESULTS_DIR}{name}/{traj_name}{iter}.traj")
                    plt.plot(xyz[0], xyz[1], xyz[2], label=traj_name, color=color, linestyle=linestyle)
            # plt.legend()
            plt.savefig(f'{PLOT_DIR + "/"}traj3D_{name}.png')
            # plt.show()
            plt.close(fig)

if __name__ == "__main__":

    # Create a directory to save the plots
    os.makedirs(PLOT_DIR, exist_ok=True)

    print("Cleaning data:")
    for name in tqdm(RESULT_NAMES):
        if "_HH_" in name or "_GV_" in name:
            clean_OIVIO_GT(f"{RESULTS_DIR}{name}")
        else:
            clean_sim_GT(f"{RESULTS_DIR}{name}")
        for traj_name in tqdm(ALGO_NAMES, leave=False):
            for iter in tqdm(ITER, leave=False):
                # print(f"Cleaning data for {name}/{traj_name}{iter}")
                clean_data(f"{RESULTS_DIR}{name}", f"{traj_name}{iter}")


    top_down_plots()
    three_d_plots()


    RPES, ATES = {}, {}

    if os.path.exists(os.path.join(PLOT_DIR, 'errors.json')):
        with open(os.path.join(PLOT_DIR, 'errors.json'), 'r') as file:
            errors = json.load(file)
            RPES, ATES = errors['RPES'], errors['ATES']

    print("Evaluating trajectory errors:")

    for name in tqdm(RESULT_NAMES):
        traj_gt = read_trajectory(f"{RESULTS_DIR}{name}/gt_traj.traj")
        for traj_name in tqdm(ALGO_NAMES, leave=False):
            local_rpes, local_ates = [], []
            for iter in tqdm(ITER, leave=False):
                if f"{name}/{traj_name}{iter}" in RPES:
                    continue

                traj_est = read_trajectory(f"{RESULTS_DIR}{name}/{traj_name}{iter}.traj")
                try:
                    rpe_result = evaluate_trajectory(traj_gt,traj_est,param_max_pairs=0)
                    rpe_trans = np.mean(np.array(rpe_result)[:,4])
                    rpe_rot = np.mean(np.array(rpe_result)[:,5])
                    local_rpes.append(rpe_trans)
                except:
                    rpe_trans = None
                    rpe_rot = None

                try:
                    ate = evaluate_ate(f"{RESULTS_DIR}{name}/gt_traj.traj", f"{RESULTS_DIR}{name}/{traj_name}{iter}.traj")
                    local_ates.append(ate)
                except:
                    ate = None

                RPES[f"{name}/{traj_name}{iter}"] = rpe_trans
                ATES[f"{name}/{traj_name}{iter}"] = ate

                # print(f"Evaluated RPE for {name}/{traj_name}{iter}: {rpe_trans}")
                # print(f"Evaluated ATE for {name}/{traj_name}{iter}: {ate}")
        
        with open(os.path.join(PLOT_DIR, 'errors.json'), 'w') as file:
            # print("Writing errors to file")
            json.dump({'RPES': RPES, 'ATES': ATES}, file, indent=2)





    rpe_result_grid, ate_result_grid = [], []

    for name in RESULT_NAMES:
        rpe_grid, ate_grid = [], []
        for baseline in [f"{ALGO_NAMES[0]}{i}" for i in ITER]:
            baseline_rpe_grid, baseline_ate_grid = [], []
            baseline_rpe, baseline_ate = RPES[f"{name}/{baseline}"], ATES[f"{name}/{baseline}"]

            for modified in [f"{ALGO_NAMES[1]}{i}" for i in ITER]:
                modified_rpe, modified_ate = RPES[f"{name}/{modified}"], ATES[f"{name}/{modified}"]
                if baseline_rpe is None or modified_rpe is None:
                    rpe_percent_improvement = 0
                else:
                    rpe_percent_improvement = round(((baseline_rpe - modified_rpe) / baseline_rpe) * 100, 2)
                
                if baseline_ate is None or modified_ate is None:
                    ate_percent_improvement = 0
                else:
                    ate_percent_improvement = round(((baseline_ate - modified_ate) / baseline_ate) * 100, 2)

                baseline_rpe_grid.append(rpe_percent_improvement)
                baseline_ate_grid.append(ate_percent_improvement)
            rpe_grid.append(baseline_rpe_grid)
            ate_grid.append(baseline_ate_grid)
        rpe_result_grid.append(rpe_grid)
        ate_result_grid.append(ate_grid)


    for error_name in ['RPE', 'ATE']:
        if error_name == 'RPE':
            results_array = np.array(rpe_result_grid)
        elif error_name == 'ATE':
            results_array = np.array(ate_result_grid)

        for i in range(len(RESULT_NAMES)):
            # Create the subplot for the current grid
            cur_results = results_array[i,:,:]
            fig, ax = plt.subplots(figsize=(10, 10))

            # Create the heatmap for the current grid
            im = ax.imshow(cur_results, cmap='coolwarm', interpolation='nearest', vmin=-100, vmax=100)

            # Add the numbers to the heatmap
            # for x in range(NUM_EVAL):
            #     for y in range(NUM_EVAL):
            #         ax.text(y, x, f"{round(results_array[i, x, y], 1)}%", ha='center', va='center', color='black')

            # Add labels and title to the subplot
            results_str = f"{error_name} | {RESULT_NAMES[i]} |  μ: {np.mean(cur_results)} | σ: {np.std(cur_results)} | max: {np.max(cur_results)} | min: {np.min(cur_results)}"
            ax.text(0, 1.1, results_str, transform=ax.transAxes, fontsize=10)
            ax.set_xlabel('Modified Estimated Trajectory')
            ax.set_ylabel('DSO Estimated Trajectory')
            ax.set_title(f'Percent Improvement in {error_name} : {RESULT_NAMES[i]}')
            fig.colorbar(im, fraction=0.046, pad=0.04)
            print(results_str)


            # Save the plot to the plot directory
            plt.savefig(f'{PLOT_DIR + "/"}{error_name}_{i}_{RESULT_NAMES[i]}.png')

            # Close the plot
            plt.close(fig)
