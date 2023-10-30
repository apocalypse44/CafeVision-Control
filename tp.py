import os
from cvzone.HandTrackingModule import HandDetector
import cv2
from flask import Flask, render_template, Response

app = Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)


modeType = 0
selections = ["Black Coffee", "Latte", "Espresso", "Coffee", "Cappuccino"]

@app.route('/')
def index():
    image_dir = 'static/images'  # Change this to your image directory
    image_list = os.listdir(image_dir)
    return render_template('test.html', image_list=image_list)

# @app.route('/')
# def index():
#     return render_template('index.html', selections=selections, modeType=modeType)

def gen_frames():
    imgBackground = cv2.imread("Resources/Background.png")
    folderPathIcons = "Resources/Icons"
    listImgIconsPath = os.listdir(folderPathIcons)
    listImgIcons = []
    for imgIconsPath in listImgIconsPath:
        listImgIcons.append(cv2.imread(os.path.join(folderPathIcons, imgIconsPath)))

    modePositions = [(1136, 196), (1000, 384), (1136, 581)]
    counterPause = 0
    selectionList = [-1, -1, -1]
    modeType = 0  # for changing selection mode
    selection = -1
    counter = 0
    selectionSpeed = 7
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)

        counterPause = 0

        if hands and counterPause == 0 and modeType < 3:
            hand1 = hands[0]
            fingers1 = detector.fingersUp(hand1)
            print(fingers1)

            if fingers1 == [0, 1, 0, 0, 0]:
                if selection != 1:
                    counter = 1
                selection = 1
            elif fingers1 == [0, 1, 1, 0, 0]:
                if selection != 2:
                    counter = 1
                selection = 2
            elif fingers1 == [0, 1, 1, 1, 0]:
                if selection != 3:
                    counter = 1
                selection = 3
            else:
                selection = -1
                counter = 0

            if counter > 0:
                counter += 1
                print(counter)

                cv2.ellipse(imgBackground, modePositions[selection - 1], (103, 103), 0, 0,
                            counter * selectionSpeed, (0, 255, 0), 20)
                if counter * selectionSpeed > 360:
                    selectionList[modeType] = selection
                    modeType += 1
                    counter = 0
                    selection = -1
                    counterPause = 1

        if counterPause > 0:
            counterPause += 1
            if counterPause > 60:
                counterPause = 0

        if selectionList[0] != -1:
            icon = listImgIcons[selectionList[0] - 1]
            img[636:636 + icon.shape[0], 133:133 + icon.shape[1]] = icon
        if selectionList[1] != -1:
            icon = listImgIcons[2 + selectionList[1]]
            img[636:636 + icon.shape[0], 340:340 + icon.shape[1]] = icon
        if selectionList[2] != -1:
            icon = listImgIcons[5 + selectionList[2]]
            img[636:636 + icon.shape[0], 542:542 + icon.shape[1]] = icon


        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
