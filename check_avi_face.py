# -*- coding: utf-8 -*-
import cv2
from imutils.video import FPS
import numpy as np
import imutils
import face_recognition
import pickle
import time
import datetime
import logging
import logging.config
import json
import config.log_config as logconf
import to_do_thread
import _thread

#def get_face_path(face_pic_path="./face_pic_path", ext=".jpg"):
#    return "{face_pic_path}/{rand}{ext}".format(face_pic_path=face_pic_path, rand=str(datetime.datetime.now())[:19], ext=ext)

# check people faces and counts
def get_all_people_face_list(all_people_names):
    people_face_count = list()
    for apn in all_people_names:
        if len(people_face_count) == 0:
            people_face_count.append({'face_name': apn, 'count': 1})
        else:
            check_people = False
            for pfc in people_face_count:
                if apn == pfc['face_name']:
                    pfc['count'] += 1
                    check_people = True
                    break
            
            if check_people is False:
                people_face_count.append({'face_name': apn, 'count': 1})
                
    str_people_face_info = ''
    for pfc in people_face_count:
        str_people_face_info += 'face:' + pfc['face_name'] + str(pfc['count']) + '; '
    
    return str_people_face_info

#if __name__=='__main__':
def to_check_face(avi_path_list):    
    
    #logging.config.dictConfig(logconf.logging_configure)
    logger = logging.getLogger('check_avi_face')
    logger.info("loading encodings + face detector...")
    #data = pickle.loads(open(args["encodings"], "rb").read())
    #detector = cv2.CascadeClassifier(args["cascade"])
    data = pickle.loads(open("/home/pi/Desktop/pi_camera_fetcher/encodings.pickle", "rb").read())
    detector = cv2.CascadeClassifier("/home/pi/Desktop/pi_camera_fetcher/haarcascade_frontalface_default.xml")

    logger.info("starting video stream...")
    
    face_info_list = list()

    for avi in avi_path_list:
        conf = json.load(open('/home/pi/Desktop/pi_camera_fetcher/conf.json'))
        
        avi_path = conf['move_video_path'] + '/' + avi
        logger.info(avi_path)
        
        vc = cv2.VideoCapture(avi_path)
        fps = FPS().start()
        
        save_face = conf['face_pic']
        all_people_names = []

        while True:
            (grabbed,frame) = vc.read()
            if frame is None:
                break
            
            frame = imutils.resize(frame,width=600)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.5)
                name = "Unknown"

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    name = max(counts, key=counts.get)

                names.append(name)
                all_people_names.append(name)

            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            if len(names) > 0 and save_face is True:
                ts = str(datetime.datetime.now())[:19]
                f = "./{face_pic_path}/{timestamp}.jpg".format(face_pic_path=conf['face_pic_path'], timestamp=ts)
                cv2.imwrite(f, frame)

                logger.info(f)
            
            if conf["show_check_face_video"]:
                cv2.imshow("frame",frame)
                
                if cv2.waitKey(50)&0xFF == ord('q'):
                    break
            fps.update()
        fps.stop()

        cv2.destroyAllWindows()
        vc.release()
        
        str_people_face_info = get_all_people_face_list(all_people_names)
        #if str_people_face_info != '':
        #logger.info(str_people_face_info)
        face_info_list.append({'avi_name': avi, 'avi_path': avi_path, 'face_info': str_people_face_info})
        #else:
        #    logger.info('no faces in videos')
    
    if len(face_info_list) > 0:
        #for face_info in face_info_list:
        #    logger.info(face_info)
        
        try:
            to_do_thread.to_send_email(face_info_list)
            #_thread.start_new_thread(to_do_thread.to_send_email,(face_info_list,))
        except Exception as e:
            logger.error(e)
            logger.error('face send email Error')


