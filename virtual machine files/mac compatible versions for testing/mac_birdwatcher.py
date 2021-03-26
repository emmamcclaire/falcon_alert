from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import schedule
import time
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow import keras
import numpy as np
from tensorflow.keras.applications.vgg19 import preprocess_input
from scipy import stats
import datetime
import csv
from shutil import copyfile
import cv2
import pytz 
GMT = pytz.timezone('GMT')
import tensorflow_hub as hub

def get_screenshots():
    global video_box_2
    video_box_2.screenshot('live_images/image1.png')
    time.sleep(1)
    video_box_2.screenshot('live_images/image2.png')
    time.sleep(1)
    video_box_2.screenshot('live_images/image3.png')

previous_status = 'start'

def is_there_a_bird():
    
    print('checking the nest ...')
    
    snapshot_time = datetime.datetime.now(GMT)
    get_screenshots()
    
    predictions = []
    for i in ['1', '2', '3']:
        screenshot = image.load_img('live_images/image' + i + '.png', target_size = (224, 224))
        screenshot_array = image.img_to_array(screenshot)
        prep_img = tf.keras.applications.mobilenet_v2.preprocess_input(screenshot_array)
        prediction = np.argmax(model.predict(prep_img[np.newaxis, ...]))
        predictions.append(prediction)

    global status
    global previous_status

    if stats.mode(predictions)[0][0] == 1:
        status = 'bird'
        
    elif stats.mode(predictions)[0][0] == 0:
        status = 'no bird'
    
    message = 'none'
    
    if status != previous_status:
        if previous_status == 'start':
            pass
        elif previous_status == 'bird' and status == 'no bird':
            message = 'BIRD LEFT'
        elif previous_status == 'no bird' and status == 'bird':
            message = 'BIRD IS BACK'
            
        previous_status = status
        
    else:
        message = f'{status} | NO CHANGE'
    
    return print(message)
            
# load model

model = load_model('models/t_model_1_4.h5', custom_objects={'KerasLayer':hub.KerasLayer})

# open falcon cam website
PATH = '/Applications/chromedriver'

# headless
from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True
options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(PATH, options=options)

driver.get('https://www.nottinghamshirewildlife.org/peregrine-cam')

elements = driver.find_elements(By.TAG_NAME, 'button')

eu_compliance = driver.find_element(By.ID, 
                                     'popup-buttons')

eu_compliance.find_elements_by_css_selector("*")[0].click()

play_buttons = driver.find_elements(By.CLASS_NAME, 'vjs-big-play-button')

play_buttons[1].click()
        
# locate video element for screenshotting
video_boxes = driver.find_elements(By.TAG_NAME, 'video')

video_box_1, video_box_2 = video_boxes
        
driver.execute_script("arguments[0].scrollIntoView();", video_box_1)
        
schedule.clear()

schedule.every(1).minutes.do(is_there_a_bird)

while True:
    schedule.run_pending()
    time.sleep(1)
