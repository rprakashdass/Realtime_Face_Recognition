import cv2
import face_recognition
import pickle
import os
import mysql.connector

db_con = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='face_attendance'
)

db_cur = db_con.cursor()


# def upload_student_to_db(name, encoding):
#     # serializing
#     encoding_bytes = pickle.dumps(encoding)
#     sql_query = "INSERT INTO storage (name, encoding) VALUES  (%s, %s)"
#     values = (name, encoding_bytes)
#     db_cur.execute(sql_query, values)
#     db_con.commit()
#

def upload_student_image_to_db(name, image_path):
    with open(image_path, 'rb') as f:
        profiles = f.read()

    sql_query = "INSERT INTO storage (name, profiles) VALUES (%s, %s)"
    values = (name, profiles)
    db_cur.execute(sql_query, values)
    db_con.commit()

    print(f"Images Uploaded to Database for {name}")


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []
encodings = []  # Create a list to store face encodings

for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    imgList.append(img)
    studentIds.append(os.path.splitext(path)[0])

    # To upload images to db
    student_id = os.path.splitext(path)[0]
    image_path = os.path.join(folderPath, path)

    upload_student_image_to_db(student_id, image_path)

    # Find face encoding for the image
    encode = face_recognition.face_encodings(img)[0]
    encodings.append(encode)  # Append the encoding to the list

    fileName = f'{folderPath}/{path}'
    # print(path)
    # print(os.path.splitext(path)[0])
print(studentIds)

# for student_id, encode in zip(studentIds, encodings):
#     upload_student_to_db(student_id, encode)

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")