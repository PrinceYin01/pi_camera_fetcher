# import the necessary packages

import os
import datetime


class TempImage:
    
    def __init__(self, email_pic_path="./email_pic_path", ext=".jpg"):

        self.path = "{email_pic_path}/{rand}{ext}".format(email_pic_path=email_pic_path, rand=str(datetime.datetime.now())[:19], ext=ext)

    def cleanup(self):

        os.remove(self.path)
