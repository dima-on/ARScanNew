import cv2
import mediapipe as mp
from PIL import Image
import os
import numpy as np
import gc
import requests
from io import BytesIO


Down_Image_Path = ['static/Photo/Down/legs.png', 'static/Photo/Down/leggins-1.png', 'static/Photo/Down/Down.png']
Top_Image_Path = ['static/Photo/Top/T_Short_Red.png', 'static/Photo/Top/T_Short_EnerGym.png', 'static/Photo/Top/Coft-removebg-preview.png', 'static/Photo/Top/top-1.png', 'static/Photo/Top/te.png', "static/Photo/Top/Top.png"]

Top_Offset_To_Y = [15, 2.8, 30, 13, 8, 20]
Top_Offset_To_X = [-2, -1, -4, -3, -4, 0]

Top_With = [1150, 1300, 1280, 800, 1150, 1100]
Top_HeightMult = [-0.15, -0.15, 0, -0.15, -0.25, -0.15]

Down_Offset_To_Y = [-30, -10, -100]
Down_Offset_To_X = [0, -1, 0]

Down_With = [1250, 1100, 1000]
Down_HeightMult = [0, 0, -0.2]

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


def get_image_size(url):
    response = requests.get(url)
    image_data = response.content

    # Открытие изображения с помощью PIL
    image = Image.open(BytesIO(image_data))

    # Получение размеров изображения
    width, height = image.size
    return width, height
def body_Detect(Index, frame, landmarks, array):
    ySize, xSize = frame.shape[:2]

    XFSize, YFSize = 640, 480
    ProcentSizeX = (1 - xSize / XFSize)


    LeftTop = (landmarks[23].y - landmarks[11].y) / 10
    LeftRight = (landmarks[24].y - landmarks[12].y) / 10

    shoulder_left = np.array([landmarks[11].x, landmarks[11].y - LeftTop])
    shoulder_right = np.array([landmarks[12].x, landmarks[12].y - LeftRight])


    distanceX = int((shoulder_left[0] - shoulder_right[0]) * array[3][Index])


    if distanceX <= 0:
        distanceX *= -1

    ClothYsize, ClothXsize = get_image_size(str(array[0][Index]))

    xSizeForNew = int(distanceX - (distanceX * ProcentSizeX))
    ySizeForNew = int(((xSizeForNew / ClothYsize) * ClothXsize) + ((xSizeForNew / ClothYsize) * ClothXsize) * array[4][Index])

    new_size = (xSizeForNew, ySizeForNew)
    offsetX = int(((xSizeForNew / 100) * array[2][Index]))
    offsetY = int(((ySizeForNew / 100) * array[1][Index]))

    PosYSholder = shoulder_left[1] * ySize
    center_x = int(((shoulder_left[0] + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2) * frame.shape[1]) + offsetX
    center_y = int((PosYSholder + (ySizeForNew / 2))) - offsetY

    overlay_position = (center_x - new_size[0] // 2, center_y - new_size[1] // 2)

    # Освободить память: удалить ненужные переменные
    XPr = (overlay_position[0] / xSize) * 100
    YPr = (overlay_position[1] / ySize) * 100

    del LeftTop, LeftRight, shoulder_left, shoulder_right, distanceX, xSizeForNew, ySizeForNew, offsetX, offsetY, PosYSholder

    return new_size, XPr, YPr


def leg_Detect(Index, frame, landmarks, array):

    ySize, xSize = frame.shape[:2]

    XFSize, YFSize = 640, 480
    ProcentSizeX = (1 - xSize / XFSize)

    pose_landmark = mp_pose.PoseLandmark

    hip_left = np.array([landmarks[pose_landmark.LEFT_HIP].x, landmarks[pose_landmark.LEFT_HIP].y])
    hip_right = np.array([landmarks[pose_landmark.RIGHT_HIP].x, landmarks[pose_landmark.RIGHT_HIP].y])
    Knee_left = np.array([landmarks[pose_landmark.LEFT_KNEE].x, landmarks[pose_landmark.LEFT_KNEE].y])

    distanceX = int((hip_left[0] - hip_right[0]) * (array[8][Index]))
    distanceY = int((hip_left[1] - Knee_left[1]) * (array[8][Index]))

    if distanceX <= 0:
        distanceX *= -1
    if distanceY <= 0:
        distanceY *= -1
    KofForSize = distanceY / distanceX

    ClothXsize, ClothYsize = get_image_size(array[5][Index])

    xSizeForNew = int(distanceX - (distanceX * ProcentSizeX))
    ySizeForNew = int(((xSizeForNew * ClothXsize) / ClothYsize) + ((xSizeForNew * ClothXsize) / ClothYsize) * array[9][Index] * KofForSize)

    print(xSizeForNew, ySizeForNew)

    new_size = (xSizeForNew, ySizeForNew)

    offsetY = int((ySizeForNew / 100) * array[6][Index])
    offsetX = int((distanceX / 100) * array[7][Index])

    center_x = int((hip_left[0] + landmarks[pose_landmark.RIGHT_HIP].x) / 2 * frame.shape[1]) + offsetX
    center_y = int((hip_left[1] + (ySizeForNew / 2))) - offsetY



    overlay_position = (center_x - new_size[0] // 2, center_y - new_size[1] // 2)
    XPr = (overlay_position[0] / xSize) * 100
    YPr = (overlay_position[1] / ySize) * 100
    # Освободить память: удалить ненужные переменные
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
                print(i)

def resImage(img, indexT, indexD, tag):
    path = "ShopBD/" + str(tag) + ".txt"
    with open(path, 'r') as file:
        content = file.read()
    array = eval(content)

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
            TopSize, XPr, YPr = body_Detect(indexT, image, landmarks, array)

        if indexD != -1:
            DownSize, XPrDown, YPrDown = leg_Detect(indexD, image, landmarks, array)

        if os.path.isfile(img):
            try:
                os.remove(img)
            except:
                print()


        pose.close()

        print(DownSize)

        gc.collect()
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return XPr, YPr, massSize, TopSize, XPrDown, YPrDown, DownSize
    else:
        os.remove(img)
        pose.close()
