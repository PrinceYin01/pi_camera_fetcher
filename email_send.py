# -*- coding: utf-8 -*-
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os
import shutil
import logging


# to send email
def to_send_email(conf, msgRoot, subject, email_text):
    sender = conf['sender']
    receiver = conf['receiver']
    smtpserver = conf['smtpserver']
    username = conf['username']
    password = conf['password']
    
    now = str(datetime.datetime.now())[:19]
    
    if subject == '':
        subject = conf['subject']
    msgRoot['Subject'] = subject + now

    if email_text == '':
        email_text = conf['email_text']
    msgText = MIMEText(email_text + now, 'html', 'utf-8')
    msgRoot.attach(msgText)
    
    smtp = None
    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msgRoot.as_string())
        
        logging.info('send email is ok')
    except Exception as e:
        logging.error(e)
    finally:
        smtp.quit()
        

# msgRoot to add image info
def msgRoot_attach_image(pic_path, picture, msgRoot):
    have_attach = 0
    try:
        if os.path.isfile(pic_path + '/' + picture):
            logging.info(picture)
            with open(pic_path + '/' + picture, 'rb') as f:
                ima = MIMEBase('image', 'jpg', filename=picture)
                ima.add_header('Content-Disposition', 'attachment', filename=picture)
                ima.add_header('Content-ID', '<0>')
                ima.add_header('X-Attachment-Id', '0')
                ima.set_payload(f.read())
                encoders.encode_base64(ima)
                msgRoot.attach(ima)
                have_attach = 1
    except Exception as e:
        logging.error(e)
    finally:
        return have_attach
        

# msgRoot to add avi info
def msgRoot_attach_videos(video_path, video, msgRoot):
    have_attach = 0
    try:
        if os.path.isfile(video_path + '/' + video):
            logging.info(video)
            att = MIMEText(open(video_path + '/' + video, 'rb').read(), 'base64', 'utf-8')
            att['Content-Type'] = "application/octet-stream"
            att['Content-Transfer-Encoding'] = "base64"
            att['Content-Disposition'] = "attachment; filename=" + video
            msgRoot.attach(att)
            have_attach = 1
    except Exception as e:
        logging.error(e)
    finally:
        return have_attach


# files move
def files_to_move_place(old_path, new_path, files):
    try:
        if os.path.isfile(old_path + '/' + files):
            if os.path.exists(new_path) is False:
                os.mkdir(new_path)
            shutil.move(old_path + '/' + files, new_path + '/' + files)
    except Exception as e:
        logging.error(e)


def send_email(conf):
    logger = logging.getLogger('email_send')
    
    msgRoot = MIMEMultipart('related')

    pictures = os.listdir(conf['move_pic_path'])    
    pictures = sorted(pictures, key=lambda x: os.path.getmtime(os.path.join(conf['move_pic_path'], x)))
    
    picture_file_count = 0
    for picture in pictures:
        have_attach = msgRoot_attach_image(conf['move_pic_path'], picture, msgRoot)
        picture_file_count += have_attach
            
    videos = os.listdir(conf['move_video_path'])    
    videos = sorted(videos, key=lambda x: os.path.getmtime(os.path.join(conf['move_video_path'], x)))
    
    avi_file_count = 0
    for avi in videos:
        have_attach = msgRoot_attach_videos(conf['move_video_path'], avi, msgRoot)
        avi_file_count += have_attach
            
    if picture_file_count == 0 and avi_file_count == 0:
        return

    try:

        to_send_email(conf, msgRoot, '', '')
        
        newdir = str(datetime.datetime.now())[:19].replace('-','')[:8]
        
        for picture in pictures:
            files_to_move_place(conf['move_pic_path'], conf['move_pic_path']+'/'+newdir, picture)
        
        for avi in videos:
            files_to_move_place(conf['move_video_path'], conf['move_video_path']+'/'+newdir, avi)
        
        logger.info('pictures or videos are transfered')
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('finish send email')


def send_email(conf, upload_move_pic_list, upload_move_videos_list):
    if len(upload_move_pic_list) == 0 and len(upload_move_videos_list) == 0:
        return
    
    logger = logging.getLogger('move_to_email_send')
    
    msgRoot = MIMEMultipart('related')
    
    for picture in upload_move_pic_list:
        msgRoot_attach_image(conf['move_pic_path'], picture, msgRoot)
    
    for avi in upload_move_videos_list:
        msgRoot_attach_videos(conf['move_video_path'], avi, msgRoot)

    try:

        to_send_email(conf, msgRoot, '', '')
        
        newdir = str(datetime.datetime.now())[:19].replace('-','')[:8]
        
        for picture in upload_move_pic_list:
            files_to_move_place(conf['move_pic_path'], conf['move_pic_path']+'/'+newdir, picture)
        
        for avi in upload_move_videos_list:
            files_to_move_place(conf['move_video_path'], conf['move_video_path']+'/'+newdir, avi)
        
        logger.info('pictures or videos are transfered')
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('finish send email')


def send_email(conf, face_info_list):
    if len(face_info_list) == 0:
        return
    logger = logging.getLogger('face_to_email_send')
    
    msgRoot = MIMEMultipart('related')
    
    newdir = str(datetime.datetime.now())[:19].replace('-','')[:8]
    
    email_text = ''
    for face_info in face_info_list:
        if face_info['face_info'] != '':
            logger.info(face_info['avi_path'])
            msgRoot_attach_videos(conf['move_video_path'], face_info['avi_name'], msgRoot)
            email_text = email_text + 'avi:' + face_info['avi_name'] + ' ; ' + face_info['face_info'] + '<br>'
        else:
            files_to_move_place(conf['move_video_path'], conf['face_video_path']+'/'+'no_face_video'+'/'+newdir, face_info['avi_name'])
            logger.info('{}:{}'.format(face_info['avi_path'],'no faces in videos'))
            
    if email_text == '':
        return
    try:
        
        to_send_email(conf, msgRoot, 'face check ', email_text)    
        
        for face_info in face_info_list:
            if face_info['face_info'] != '':
                files_to_move_place(conf['move_video_path'], conf['face_video_path']+'/'+newdir, face_info['avi_name'])
            #else:
            #    files_to_move_place(conf['move_video_path'], conf['face_video_path']+'/'+'no_face_video'+'/'+newdir, face_info['avi_name'])
        logger.info('pictures or videos are transfered')
    except Exception as e:
        logger.error(e)
    finally:
        logger.info('finish send email')

