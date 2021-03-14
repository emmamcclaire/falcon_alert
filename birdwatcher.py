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

def get_screenshots():
    global video_box
    video_box.screenshot('live_images/image1.png')
    time.sleep(1)
    video_box.screenshot('live_images/image2.png')
    time.sleep(1)
    video_box.screenshot('live_images/image3.png')

def is_there_a_bird():
    
    snapshot_time = datetime.datetime.now()
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
                     'saved_positives/' + 
                      str(snapshot_time).replace(' ', '').replace(':', '-').replace('.', '') + '-' + i + '.png')

    if stats.mode(predictions)[0][0] == 0:
        status = 'bird'
        
    elif stats.mode(predictions)[0][0] == 1:
        status = 'no bird'
        
    with open('bird_sightings.csv', 'a', newline='') as csvfile:
        status_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        status_writer.writerow([status, snapshot_time])
        
model = load_model('models/model_1.h5')

PATH = '/Applications/chromedriver'

driver = webdriver.Chrome(PATH)
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

for i, j in enumerate(video_boxes):
    if i == 1:
        video_box = j
        
schedule.clear()

schedule.every(1).minutes.do(is_there_a_bird)

while True:
    schedule.run_pending()
    time.sleep(1)
