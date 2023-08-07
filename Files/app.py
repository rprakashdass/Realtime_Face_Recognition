import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import mysql.connector
from datetime import datetime
from flask import render_template, Flask, Response
import atexit

db_connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='face_attendance'
)

db_cursor = db_connection.cursor()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0  # active mode
counter = 0  # to download data only once
rn = -1
imgStudent = []

app = Flask(__name__)


def gen(imgBackground):
    # imgStudent = None
    global counter, modeType

    while True:
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    print(studentIds[matchIndex])
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    rn = studentIds[matchIndex]

                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        cv2.imshow("Face Attendance", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 1

            if counter != 0:

                if counter == 1:
                    # Get the Data from MySQL database
                    sql_query = "SELECT * FROM students WHERE rollnumber = %s"
                    db_cursor.execute(sql_query, (rn,))
                    studentInfo = db_cursor.fetchone()
                    print(studentInfo)

                    image_filename = f"{rn}.jpg"
                    image_path = os.path.join("Images", image_filename)
                    if os.path.exists(image_path):
                        imgStudent = cv2.imread(image_path)

                    # Update data of attendance
                    last_attendance_time_str = studentInfo[3]
                    datetimeObject = last_attendance_time_str
                    print(datetimeObject)
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondsElapsed)

                    if secondsElapsed > 30:
                        # Increment the total_attendance count and update last_attendance_time
                        sql_query = "UPDATE students SET last_attendance_time = NOW() WHERE rollnumber = %s"
                        db_cursor.execute(sql_query, (rn,))
                        db_connection.commit()
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if modeType != 3:

                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        # cv2.putText(imgBackground, str(studentInfo[4]), (861, 125),
                        #             cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(rn), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo[2]), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        # cv2.putText(imgBackground, str(studentInfo[5]), (910, 625),
                        #             cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        # cv2.putText(imgBackground, str(studentInfo[6]), (1025, 625),
                        #             cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        # cv2.putText(imgBackground, str(studentInfo[3]), (1125, 625),
                        #             cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo[1], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo[1]), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        # Resize imgStudent to fit the target region
                        # imgStudent = cv2.resize(imgStudent, (216, 216))
                        # imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        cv2.imshow("Face Attendance", imgBackground)
        cv2.waitKey(1)
        _, frame = cv2.imencode('.jpg', imgBackground)
        frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen(imgBackground), mimetype='multipart/x-mixed-replace; boundary=frame')


def release_camera():
    cap.release()
    cv2.destroyAllWindows()


atexit.register(release_camera)

if __name__ == '__main__':
    app.run(debug=True)
