# -*- coding: utf-8 -*-
from imutils import paths
import face_recognition
#import argparse
import pickle
import cv2
import os
import config.log_config as logconf
import logging
import logging.config

if __name__ == '__main__':
    logging.config.dictConfig(logconf.logging_configure)
    logger = logging.getLogger('encode_faces')
    
    logger.info('****************************** START ******************************')
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-i", "--dataset", required=True, help="path to input directory of faces + images")
    #ap.add_argument("-e", "--encodings", required=True, 	help="path to serialized db of facial encodings")
    #ap.add_argument("-d", "--detection-method", type=str, default="cnn", help="face detection model to use: either `hog` or `cnn`")
    #args = vars(ap.parse_args())

    logger.info("[INFO] quantifying faces...")
    #imagePaths = list(paths.list_images(args["dataset"]))
    imagePaths = list(paths.list_images("dataset"))

    knownEncodings = []
    knownNames = []

    for (i, imagePath) in enumerate(imagePaths):

        logger.info("[INFO] processing image {}/{}".format(i + 1,	len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        #boxes = face_recognition.face_locations(rgb, model=args["detection_method"])
        boxes = face_recognition.face_locations(rgb, model="hog")

        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:

            knownEncodings.append(encoding)
            knownNames.append(name)

    # dump the facial encodings + names to disk
    logger.info("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    #f = open(args["encodings"], "wb")
    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()
