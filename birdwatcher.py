from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import schedule
import time
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow import keras
import numpy as np
from tensorflow.keras.applications.vgg19 import preprocess_input
from scipy import stats
import datetime
import csv
from shutil import copyfile
import pytz 
GMT = pytz.timezone('GMT')

def get_screenshots():
    global video_box_2
    video_box_2.screenshot('live_images/image1.png')
    time.sleep(1)
    video_box_2.screenshot('live_images/image2.png')
    time.sleep(1)
    video_box_2.screenshot('live_images/image3.png')

def is_there_a_bird():
    
    snapshot_time = datetime.datetime.now(GMT)
    get_screenshots()
    
    predictions = []
    for i in ['1', '2', '3']:
        test_image = image.load_img('live_images/image' + i + '.png', target_size = (256, 256))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis = 0)
        test_image = preprocess_input(test_image)
        prediction = np.argmax(model.predict(test_image), axis = -1)
        predictions.append(prediction)
        if prediction == 0:
            copyfile('live_images/image' + i + '.png',
                     'per_imgs/saved_positives/' + 
                      str(snapshot_time).replace(' ', '').replace(':', '-').replace('.', '') + '-' + i + '.png')
        elif prediction == 1:
            copyfile('live_images/image' + i + '.png',
                     'per_imgs/saved_negatives/' + 
                      str(snapshot_time).replace(' ', '').replace(':', '-').replace('.', '') + '-' + i + '.png')

    if stats.mode(predictions)[0][0] == 0:
        status = 'bird'
        
    elif stats.mode(predictions)[0][0] == 1:
        status = 'no bird'
        
    with open('bird_sightings.csv', 'a', newline='') as csvfile:
        status_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        status_writer.writerow([status, snapshot_time])

# load model

model = load_model('models/model_3.h5')

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

video_buttons = []
for i in elements:
    if i.text == 'Play Video':
        video_buttons.append(i)

# start the second (zoomed in) live stream
for i, j in enumerate(video_buttons):
    if i == 1:
        j.click()
        
# locate video element for screenshotting
video_boxes = driver.find_elements(By.TAG_NAME, 'video')

video_box_1, video_box_2 = video_boxes
        
driver.execute_script("arguments[0].scrollIntoView();", video_box_1)
        
schedule.clear()

schedule.every(1).minutes.do(is_there_a_bird)

while True:
    schedule.run_pending()
    time.sleep(1)
