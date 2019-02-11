# -*- coding: utf-8 -*-

from pyimagesearch.keyclipwriter import keyclipwriter
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import to_do_thread
import check_avi_face
import _thread
import config.log_config as logconf
import logging
import logging.config


if __name__=='__main__':
    
    logging.config.dictConfig(logconf.logging_configure)
    logger = logging.getLogger('pi_surveillance')
    
    logger.info('****************************** START ******************************')
    
    warnings.filterwarnings("ignore")
    conf = json.load(open('/home/pi/Desktop/pi_camera_fetcher/conf.json'))
    
    #if conf['email_pic'] is True or conf['email_video'] is True:
    # open then thread and send email by each five minutes
    #try:
    #    _thread.start_new_thread(to_do_thread.get_net,('to_do_thread',))
    #    logger.info('open then thread and send email by each five minutes')
    #except:
    #    logger.error('Error')

    camera = PiCamera()
    camera.resolution = tuple(conf["resolution"])
    camera.framerate = conf["fps"]
    rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

    logger.info("[INFO] warming up...")
    time.sleep(conf["camera_warmup_time"])
    avg = None
    lastUploaded = datetime.datetime.now()
    send_email_time = datetime.datetime.now()
    need_send_email = False
    motionCounter = 0
    
    upload_move_pic_list = []
    upload_move_videos_list = []
    
    kcw = keyclipwriter(bufsize=16)
    consecFrames = 0

    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        conf = json.load(open('/home/pi/Desktop/pi_camera_fetcher/conf.json'))

        frame = f.array
        timestamp = datetime.datetime.now()
        text = "Unoccupied"
        
        updateConsecFrames = True

        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if avg is None:
            logger.info("[INFO] starting background model...")
            avg = gray.copy().astype("float")
            rawCapture.truncate(0)
            continue
        
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        for c in cnts:
            if cv2.contourArea(c) < conf["min_area"]:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

        ts = str(timestamp)[:19]
        #cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        if text == "Occupied":
            if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
                motionCounter += 1
                
                ts2 = str(datetime.datetime.now())[:19].replace(' ','_')
                
                if motionCounter >= conf["min_motion_frames"]:
                    if conf["move_pic"]:
                        need_send_email = True
                        send_email_time = timestamp
                        p = "{}/{}.jpg".format(conf['move_pic_path'], ts2)
                        cv2.imwrite(p, frame)
                        #cv2.imwrite(conf['move_pic_path']+'/'+ts2+'.jpg', frame)
                        logger.info("[UPLOAD PIC] {}".format(p))
                        upload_move_pic_list.append("{}.jpg".format(ts2))
                        
                    lastUploaded = timestamp
                    motionCounter = 0
                
                if conf["move_video"]:
                    consecFrames = 0
                        
                    if not kcw.recording:
                        need_send_email = True
                        send_email_time = timestamp
                        
                        p = "{}/{}.avi".format(conf['move_video_path'], ts2)
                        kcw.start(p, cv2.VideoWriter_fourcc(*'MJPG'),8)
                        logger.info("[UPLOAD VIDEOS] {}".format(p))
                        upload_move_videos_list.append("{}.avi".format(ts2))

        else:
            if need_send_email is True and (timestamp - send_email_time).seconds > 20:
                if conf['send_email'] == 1:
                    try:
                        #_thread.start_new_thread(to_do_thread.to_send_email,('to_do_thread',))
                        _thread.start_new_thread(to_do_thread.to_send_email,(upload_move_pic_list, upload_move_videos_list,))
                        #logger.info('open then thread and send email by each 10 seconds')
                        upload_move_pic_list = []
                        upload_move_videos_list = []
                    except Exception as e:
                        logger.error(e)
                        logger.error('move send email Error')
                elif conf['send_email'] == 2:
                    try:
                        _thread.start_new_thread(check_avi_face.to_check_face,(upload_move_videos_list,))
                        #logger.info(upload_move_videos_list)
                        #logger.info('open then thread and check face to send email by each 10 seconds')
                        upload_move_videos_list = []
                    except Exception as e:
                        logger.error(e)
                        logger.error('check face Error')
                send_email_time = timestamp
                need_send_email = False
            motionCounter = 0
        
        if conf["move_video"]:
            if updateConsecFrames:
                consecFrames += 1
                
            kcw.update(frame)
            
            if kcw.recording and consecFrames == 16:
                kcw.finish()

        if conf["show_video"]:
            cv2.imshow("Security Feed", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        rawCapture.truncate(0)
        
    if kcw.recording and conf["show_video"]:
        kcw.finish()

 
