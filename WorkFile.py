import cv2
import mediapipe as mp
from PIL import Image
import os
import numpy as np
import time
import gc


Down_Image_Path = ['static/Photo/Down/legs.png', 'static/Photo/Down/leggins-1.png']
Top_Image_Path = ['static/Photo/Top/T_Short_White.png', 'static/Photo/Top/T_Short_Red.png', 'static/Photo/Top/T_Short_EnerGym.png', 'static/Photo/Top/Coft-removebg-preview.png', 'static/Photo/Top/top-1.png', 'static/Photo/Top/te.png']




Top_Offset_To_Y = [10, 10, 3, 0, 55, 0]
Top_Offset_To_X = [0, -2, -1, -2, -3, 0]

Top_With = [1050, 1150, 1300, 1280, 400, 1000]
Top_Height = [550, 550, 1000, 820, 300, 500]
Top_HeightMult = [0, -0.15, -0.15, 0, 0, 0]


Down_Offset_To_Y = [-30, -10]
Down_Offset_To_X = [0, -1]

Down_With = [3200, 1100]
Down_Height = [600, 450]

Down_overlay_image = []
Top_overlay_image = []



def BeginFun():


    Count_For = 0
    for im in Down_Image_Path:
        Down_overlay_image.append(1)
        Down_overlay_image[Count_For] = Image.open(im)
        Count_For += 1
        

    Count_For = 0
    for im in Top_Image_Path:
        Top_overlay_image.append(1)
        Top_overlay_image[Count_For] = Image.open(im)
        Count_For += 1


mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


def body_Detect(Index, frame, landmarks):
    hie = time.time()
    ySize, xSize = frame.shape[:2]

    XFSize, YFSize = 640, 480
    ProcentSizeX = (1 - xSize / XFSize)
    ProcentSizeXOffSet = (xSize / XFSize)
    ProcentSizeYOffSet = (ySize / YFSize)

    LeftTop = (landmarks[23].y - landmarks[11].y) / 10
    LeftRight = (landmarks[24].y - landmarks[12].y) / 10

    shoulder_left = np.array([landmarks[11].x, landmarks[11].y - LeftTop])
    shoulder_right = np.array([landmarks[12].x, landmarks[12].y - LeftRight])

    hip_left = landmarks[23]

    distanceX = int((shoulder_left[0] - shoulder_right[0]) * Top_With[Index])
    distanceY = int((hip_left.y - shoulder_left[1]) * int(Top_Height[Index]))

    if distanceX <= 0:
        distanceX *= -1

    ClothYsize, ClothXsize = Top_overlay_image[Index].size

    xSizeForNew = int(distanceX - (distanceX * ProcentSizeX))
    ySizeForNew = int(((xSizeForNew / ClothYsize) * ClothXsize) + ((xSizeForNew / ClothYsize) * ClothXsize) * Top_HeightMult[Index])

    new_size = (max(100, xSizeForNew), max(100, ySizeForNew))
    offsetX = int(((distanceX / 100) * Top_Offset_To_X[Index]) * ProcentSizeXOffSet)
    offsetY = int(((distanceY / 100) * Top_Offset_To_Y[Index]) * ProcentSizeYOffSet)

    PosYSholder = shoulder_left[1] * ySize
    center_x = int(((shoulder_left[0] + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2) * frame.shape[1]) + offsetX
    center_y = int((PosYSholder + (ySizeForNew / 2))) - offsetY

    overlay_position = (center_x - new_size[0] // 2, center_y - new_size[1] // 2)

    # Освободить память: удалить ненужные переменные
    XPr = (overlay_position[0] / xSize) * 100
    YPr = (overlay_position[1] / ySize) * 100

    del LeftTop, LeftRight, shoulder_left, shoulder_right, hip_left, distanceX, distanceY, xSizeForNew, ySizeForNew, offsetX, offsetY, PosYSholder

    return new_size, XPr, YPr


def leg_Detect(Index, frame, landmarks):

    ySize, xSize = frame.shape[:2]

    XFSize, YFSize = 640, 480
    ProcentSizeX = (1 - xSize / XFSize)
    ProcentSizeXOffSet = (xSize / XFSize)
    ProcentSizeYOffset = (ySize / YFSize)
    pose_landmark = mp_pose.PoseLandmark
    hip_left = np.array([landmarks[pose_landmark.LEFT_HIP].x, landmarks[pose_landmark.LEFT_HIP].y])
    hip_right = np.array([landmarks[pose_landmark.RIGHT_HIP].x, landmarks[pose_landmark.RIGHT_HIP].y])
    Heel_LeftY = landmarks[pose_landmark.LEFT_ANKLE].y


    distanceX = int(((hip_left[0] - hip_right[0]) * (Down_With[Index]) * 1.2))
    distanceY = int((Heel_LeftY - hip_left[0]) * (Down_Height[Index]))

    if distanceX <= 0:
        distanceX *= -1

    ClothYsize, ClothXsize = Top_overlay_image[Index].size

    xSizeForNew = int(distanceX - (distanceX * ProcentSizeX))
    ySizeForNew = int(((xSizeForNew * ClothYsize) / ClothXsize) + ((xSizeForNew * ClothYsize) / ClothXsize) * 0)

    new_size = (max(100, xSizeForNew), max(100, ySizeForNew))

    offsetY = int((distanceY / 100) * Down_Offset_To_Y[Index] * ProcentSizeYOffset)
    offsetX = int((distanceX / 100) * Down_Offset_To_X[Index] * ProcentSizeXOffSet)

    center_x = int((hip_left[0] + landmarks[pose_landmark.RIGHT_HIP].x) / 2 * frame.shape[1]) + offsetX
    center_y = int(((hip_left[1] + landmarks[pose_landmark.LEFT_HIP].y) / 2) * frame.shape[0]) - offsetY

    overlay_position = (center_x - new_size[0] // 2, center_y - new_size[1] // 2)
    XPr = (overlay_position[0] / xSize) * 100
    YPr = (overlay_position[1] / ySize) * 100
    # Освободить память: удалить ненужные переменные
    del landmarks, hip_left, hip_right, Heel_LeftY, distanceX, distanceY, ClothYsize, ClothXsize, xSizeForNew, ySizeForNew, offsetY, offsetX, center_x, center_y

    return new_size, XPr, YPr


def delAll():
    filesRoot = os.listdir("static/")
    for i in filesRoot:
        if i != "Photo" and i != "Input":
            path = "static/" + i
            try:
                os.remove(path)
            except:
                print(i)

def resImage(img, indexT, indexD):
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
            TopSize, XPr, YPr = body_Detect(indexT, image, landmarks)

        if indexD != -1:
            DownSize, XPrDown, YPrDown = leg_Detect(indexD, image, landmarks)





        if os.path.isfile(img):
            try:
                os.remove(img)
            except:
                print()


        pose.close()

        gc.collect()
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return XPr, YPr, massSize, TopSize, XPrDown, YPrDown, DownSize
    else:
        os.remove(img)
        pose.close()
