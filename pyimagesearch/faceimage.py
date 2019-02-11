import os
import datetime


class FaceImage:
    def __init__(self, face_pic_path="./face_pic_path", ext=".jpg"):
        self.path = "{face_pic_path}/{rand}{ext}".format(face_pic_path=face_pic_path, rand=str(datetime.datetime.now())[:19], ext=ext)

    def cleanup(self):
        os.remove(self.path)
