import os
import shutil
import zipfile
import re
import sys


SPELUNK_PATH = "/home/ryanslocum/workspace/Spelunk/build/apps/spelunk"
RUN_DATA_PATH = "/home/ryanslocum/workspace/run_data"
CALIB_PATH = "/home/ryanslocum/workspace/lightDSO/spelunkCalib"


def pipeline(run_data_name):
    if len(os.listdir(SPELUNK_PATH)) < 10:
        print("Looks like there's nothing here...")
        return  

    if os.path.isdir(os.path.join(RUN_DATA_PATH, run_data_name)):
        print(f"The target directory already exists")
        return 

    for filename in os.listdir(SPELUNK_PATH):
        if filename.endswith(".jpg") and not re.match(r'color_\d{6}_left\.jpg', filename):
            os.remove(os.path.join(SPELUNK_PATH, filename))


    for filename in os.listdir(SPELUNK_PATH):
        if filename.endswith(".jpg"):
            new_filename = re.search(r'\d{6}', filename).group() + '.jpg'
            os.rename(os.path.join(SPELUNK_PATH, filename), os.path.join(SPELUNK_PATH, new_filename))


    with zipfile.ZipFile(os.path.join(SPELUNK_PATH, 'images.zip'), 'w') as zipf:
        for filename in os.listdir(SPELUNK_PATH):
            if filename.endswith(".jpg"):
                zipf.write(os.path.join(SPELUNK_PATH, filename), arcname=filename)


    os.makedirs(os.path.join(RUN_DATA_PATH, run_data_name))
    shutil.copy(os.path.join(SPELUNK_PATH, 'images.zip'), os.path.join(RUN_DATA_PATH, run_data_name))
    shutil.copy(os.path.join(SPELUNK_PATH, 'poses.csv'), os.path.join(RUN_DATA_PATH, run_data_name))
    shutil.copy(os.path.join(SPELUNK_PATH, 'times.txt'), os.path.join(RUN_DATA_PATH, run_data_name))
    shutil.copy(os.path.join(CALIB_PATH, 'camera.txt'), os.path.join(RUN_DATA_PATH, run_data_name))


    for filename in os.listdir(SPELUNK_PATH):
        if filename.endswith(".jpg"):
            os.remove(os.path.join(SPELUNK_PATH, filename))
    os.remove(os.path.join(SPELUNK_PATH, 'images.zip'))
    os.remove(os.path.join(SPELUNK_PATH, 'poses.csv'))
    os.remove(os.path.join(SPELUNK_PATH, 'times.txt'))

    print("successful save to", os.path.join(RUN_DATA_PATH, run_data_name))
    # print("setting os.environ['CURRENT_RUN_DIR'] to", run_data_name)
    # os.environ["CURRENT_RUN_DIR"] = run_data_name




if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("This script requires one argument, the name of the new run")
    else:
        pipeline(sys.argv[1])



