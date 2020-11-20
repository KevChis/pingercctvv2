# coding=utf-8
import subprocess
from subprocess import PIPE
import sys
import threading
from queue import Queue
import csv

# If no camera text file is passed as an argument then all cameras are tested
# See files in cam sub-folder for possible camera lists

# queue is used for threading queue
# broken_cameras holds a list of cameras not pingable
queue = Queue()
broken_cameras = []

# checks if camera file was passed as argument, if not then all cameras are checked
if len(sys.argv) > 1:
    camlist = sys.argv[1]
else:
    camlist = 'cameras.txt'


# function to ping camera
def camera_ping(camera):
    if subprocess.call(['ping', '-c', '1', camera], stdout=PIPE):
        return False
    else:
        return True


# function to fill queue with cameras to be tested
def fill_queue(camlist1):
    with open(f'cams/{camlist1}', 'r') as cameralist:
        for camera in cameralist:
            queue.put(camera)


def fill_camera_details():

    with open('cams/camdetails.csv', 'r') as csv_file:
        all_cameras_cctv = []
        reader = csv.reader(csv_file)

        for row in reader:
            cam = {'camera Name': row[0], 'area': row[1], 'ip address': row[2], 'location': row[3]}

            all_cameras_cctv.append(cam)
    return all_cameras_cctv


def fill_camera_queue(all_cameras):
    for cam in all_cameras:
        for k, v in cam.items():
            if 'ip address' == k:
                queue.put(v)


def show_camera_details(cameras1, broken_cams):
    for broken in broken_cams:
        for cam in cameras1:
            for k, v in cam.items():
                if 'ip address' == k and v == broken:
                    print(f'{cam}')


# worker function that pulls camera from queue and calls ping function
def worker():
    while not queue.empty():
        camera = queue.get()
        if not camera_ping(camera):
            # print(f"Camera at {camera.rstrip()} Not Responding")
            broken_cameras.append(camera)


# calls the function to fill the queue
cameras = fill_camera_details()
fill_camera_queue(cameras)


# fill_queue(camlist)


# thread_list holds running threads so it can be tested for 0 when finished
# this is internal function
thread_list = []

# sets the number of consecutive threads to run and assigns worker function as the threadable target
for t in range(300):
    thread = threading.Thread(target=worker)
    thread_list.append(thread)

# starts all available threads
for thread in thread_list:
    thread.start()

# waits for all threads to finish before going to last print message
for thread in thread_list:
    thread.join()

# prints out list of broken cameras at end
# at the moment the worker function also prints a message

show_camera_details(cameras, broken_cameras)
# print("Non responsive cameras are: ", broken_cameras)
