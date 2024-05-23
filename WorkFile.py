import time

import cv2
import mediapipe as mp
from PIL import Image
import os
import numpy as np
import gc
import requests
from io import BytesIO
import util_save






mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def get_image_size(url):
    response = requests.get(url)
    image_data = response.content

    # Открытие изображения с помощью PIL
    image = Image.open(BytesIO(image_data))

    # Получение размеров изображения
    width, height = image.size
    return width, height

def body_Detect(Index, frame, landmarks, data):
    ySize, xSize = frame.shape[:2]

    XFSize, YFSize = 640, 480
    ProcentSizeX = (1 - xSize / XFSize)


    LeftTop = (landmarks[23].y - landmarks[11].y) / 10
    LeftRight = (landmarks[24].y - landmarks[12].y) / 10

    shoulder_left = np.array([landmarks[11].x, landmarks[11].y - LeftTop])
    shoulder_right = np.array([landmarks[12].x, landmarks[12].y - LeftRight])


    distanceX = int((shoulder_left[0] - shoulder_right[0]) * data["top_width"][Index])


    if distanceX <= 0:
        distanceX *= -1

    ClothYsize, ClothXsize = get_image_size(str(data["top_link"][Index]))

    xSizeForNew = int(distanceX - (distanceX * ProcentSizeX))
    ySizeForNew = int(((xSizeForNew / ClothYsize) * ClothXsize) + ((xSizeForNew / ClothYsize) * ClothXsize) * data["top_height"][Index])

    new_size = (xSizeForNew, ySizeForNew)
    offsetX = int(((xSizeForNew / 100) * data["top_x_offset"][Index]))
    offsetY = int(((ySizeForNew / 100) * data["top_y_offset"][Index]))

    center_x = int(((shoulder_left[0] + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2) * frame.shape[1]) + offsetX
    center_y = int(((shoulder_left[1] + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2) * frame.shape[0]) - offsetY

    overlay_position = (center_x - new_size[0] // 2, center_y - new_size[1] // 2)

    # Освободить память: удалить ненужные переменные
    XPr = (overlay_position[0] / xSize) * 100
    YPr = (overlay_position[1] / ySize) * 100

    del LeftTop, LeftRight, shoulder_left, shoulder_right, distanceX, xSizeForNew, ySizeForNew, offsetX, offsetY
    return new_size, XPr, YPr


def leg_Detect(Index, frame, landmarks, data):

    ySize, xSize = frame.shape[:2]

    XFSize, YFSize = 640, 480
    ProcentSizeX = (1 - xSize / XFSize)

    pose_landmark = mp_pose.PoseLandmark

    hip_left = np.array([landmarks[pose_landmark.LEFT_HIP].x, landmarks[pose_landmark.LEFT_HIP].y])
    hip_right = np.array([landmarks[pose_landmark.RIGHT_HIP].x, landmarks[pose_landmark.RIGHT_HIP].y])
    heel_left = np.array([landmarks[pose_landmark.LEFT_ANKLE].x, landmarks[pose_landmark.LEFT_ANKLE].y])

    distanceX = int((hip_left[0] - hip_right[0]) * (data["down_width"][Index]))
    distanceY = int((hip_left[1] - heel_left[1]) * (data["down_width"][Index]))

    if distanceX <= 0:
        distanceX *= -1
    if distanceY <= 0:
        distanceY *= -1

    kof_len_leg = (distanceY * ySize) / (distanceX * xSize)
    ClothXsize, ClothYsize = get_image_size(data["down_link"][Index])

    xSizeForNew = int(distanceX - (distanceX * ProcentSizeX))
    ySizeForNew = int((((xSizeForNew / ClothYsize) * ClothXsize) + ((xSizeForNew / ClothYsize) * ClothXsize) * data["down_height"][Index]) * kof_len_leg)

    new_size = (xSizeForNew, ySizeForNew)

    offsetY = int((ySizeForNew / 100) * data["down_y_offset"][Index])
    offsetX = int((xSizeForNew / 100) * data["down_x_offset"][Index])

    center_x = int((hip_left[0] + landmarks[pose_landmark.RIGHT_HIP].x) / 2 * frame.shape[1]) + offsetX
    center_y = int((hip_left[1] + landmarks[pose_landmark.RIGHT_HIP].y) / 2 * frame.shape[0] - offsetY)



    overlay_position = (center_x - new_size[0] // 2, center_y - new_size[1] // 2)
    XPr = (overlay_position[0] / xSize) * 100
    YPr = (overlay_position[1] / ySize) * 100

    del landmarks, hip_left, hip_right, distanceX, ClothYsize, ClothXsize, xSizeForNew, ySizeForNew, offsetY, offsetX, center_x, center_y

    return new_size, XPr, YPr


def delAll():
    filesRoot = os.listdir("static/")
    for i in filesRoot:
        if i != "Photo" and i != "Input":
            path = "static/" + i
            try:
                os.remove(path)
            except:
                pass

def resImage(img, indexT, indexD, tag):
    path = "ShopBD/" + str(tag) + ".json"
    data = util_save.open_jsonAll(path)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    image = cv2.imread(img)

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb_image)

    XPr, YPr, TopSize = 0, 0, 0
    XPrDown, YPrDown, DownSize = 0, 0, 0

    ySize, xSize = image.shape[:2]
    massSize = [xSize, ySize]

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        if indexT != -1:
            TopSize, XPr, YPr = body_Detect(indexT, image, landmarks, data)

        if indexD != -1:
            DownSize, XPrDown, YPrDown = leg_Detect(indexD, image, landmarks, data)

        if os.path.isfile(img):
            try:
                os.remove(img)
            except:
                pass


        pose.close()
        del results


        gc.collect()
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        tup_return = [XPr, YPr, massSize, TopSize, XPrDown, YPrDown, DownSize]
        return tup_return
    else:
        os.remove(img)
        pose.close()
