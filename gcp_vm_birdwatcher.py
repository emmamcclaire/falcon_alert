from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import time
from io import BytesIO
import pytz
GMT = pytz.timezone('GMT')
import datetime
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import tensorflow_hub as hub
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
import schedule
import psycopg2

previous_status = 'start'

def get_screenshot(num:str):
   
    img = driver.get_screenshot_as_png()

    img = Image.open(BytesIO(img))
    
    left = 510
    top = 570
    right = 1395
    bottom = 1060
    img_c = img.crop((int(left), int(top), int(right), int(bottom)))
    img_c.save('screenshot_'+num+'.png')

def write_to_psql(data):
    conn = psycopg2.connect(
            database='postgres', user = 'postgres', password = 'nottperegrine',
            host = '127.0.0.1', port = '5432'
            )

    conn.autocommit = True

    cursor = conn.cursor()

    SQL = '''INSERT INTO sightings (observation, time_gmt, model_version)
            VALUES (%s, %s, %s);
            '''
    cursor.execute(SQL, data)
    
    conn.commit()
    conn.close()

def is_there_a_bird():
    print('checking the nest...')
    snapshot_time = f'{datetime.datetime.now(GMT):%Y-%m-%d %H:%M:%S}'
    get_screenshot('1')
    time.sleep(30)
    get_screenshot('2')
    time.sleep(30)
    get_screenshot('3')
    
    predictions = []

    for i in ['1', '2', '3']:

        screenshot = image.load_img('screenshot_'+i+'.png', target_size = (224, 224))
        screenshot_array = image.img_to_array(screenshot)
        prep_img = tf.keras.applications.mobilenet_v2.preprocess_input(screenshot_array)
        prediction = np.argmax(model.predict(prep_img[np.newaxis, ...]))
        predictions.append(prediction)

    print(predictions)

    global status
    global previous_status
    
    if 1 not in predictions:
        status = 'no bird'

    elif 1 in predictions:
        status = 'bird'
    
    data = (status, snapshot_time, model_ver)
    write_to_psql(data)

    return print(snapshot_time + ' | ' + status)

model_ver = 'model_1_6'
model = load_model('models/'+model_ver+'.h5', custom_objects={'KerasLayer':hub.KerasLayer})

# The place we will direct our WebDriver to
url = 'https://www.nottinghamshirewildlife.org/peregrine-cam'

from selenium.webdriver.chrome.options import Options
options = Options()
options.headless = True
options.add_argument("--window-size=1920x1080")
# Creating the WebDriver object using the ChromeDriver
driver = webdriver.Chrome(options = options)

# Directing the driver to the defined url
driver.get(url)

try:
    eu_compliance = driver.find_element(By.ID,
                                     'popup-buttons')

    eu_compliance.find_elements_by_css_selector("*")[0].click()

    video_boxes = driver.find_elements(By.TAG_NAME, 'video')

    video_box_1, video_box_2 = video_boxes

    driver.execute_script("arguments[0].scrollIntoView();", video_box_1)

    time.sleep(5)

    play_buttons = driver.find_elements(By.CLASS_NAME,
                                     'vjs-big-play-button')

    play_buttons[1].click()
    
    time.sleep(5)

    print('page loaded')

    schedule.every(1).minutes.do(is_there_a_bird)

    while True:
        schedule.run_pending()
        time.sleep(1)

    driver.quit()

except Exception as e:
    print('exception - driver quit early')
    print(e)
    driver.quit()

print('driver quit')


