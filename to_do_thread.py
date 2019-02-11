import _thread
import time
import psutil
import email_send
import logging
import json


def get_net(thread_name):
    logger = logging.getLogger(thread_name)
    #logger.info(thread_name)
    while 1:
        conf = json.load(open('conf.json'))
        nis = psutil.net_if_stats()['wlan0']
        if nis.isup:
            # logger.info('net is ok')
            email_send.send_email(conf)
            
            time.sleep(60)
        else:
            logger.error('net is error')
            time.sleep(30)


def to_send_email(thread_name):
    conf = json.load(open('/home/pi/Desktop/pi_camera_fetcher/conf.json'))
    email_send.send_email(conf)


def to_send_email(upload_move_pic_list, upload_move_videos_list):
    conf = json.load(open('/home/pi/Desktop/pi_camera_fetcher/conf.json'))
    email_send.send_email(conf, upload_move_pic_list, upload_move_videos_list)


def to_send_email(face_info_list):
    conf = json.load(open('/home/pi/Desktop/pi_camera_fetcher/conf.json'))
    email_send.send_email(conf, face_info_list)
    
