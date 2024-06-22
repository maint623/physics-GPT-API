from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

import os

import chrome_handler
import helper_funcs
import sys

from flask import Flask, request, jsonify
app = Flask(__name__)

# current file path
current_file_path = os.path.dirname(os.path.realpath(__file__))
user_data_folder = current_file_path + "/chromedata"
chrome_profile = "Default"

lastMessage = "null"

def load_chrome():
    service = Service(os.getcwd() + "/chromedriver")

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"--user-data-dir={user_data_folder}")
    chrome_options.add_argument(f'--profile-directory={chrome_profile}')

    global helper_fn, driver
    driver = uc.Chrome(service=service,chrome_options=chrome_options)
    helper_fn = helper_funcs.HelperFn(driver)

def start_chat_gpt():
    load_chrome()
    driver.get("https://chat.openai.com/chat")

def send(response_xpath):
    global lastMessage
    if helper_fn.is_element_present(response_xpath):
        response = helper_fn.find_elements(response_xpath)[-1].text
        if(lastMessage == response):
            time.sleep(2)
            return send(response_xpath)
        else:
            lastMessage = response
            return response
    else:
        return "null"
    
def make_gpt_request(text):
    text_area_xpath = "//*[@id='prompt-textarea']"
    helper_fn.wait_for_element(text_area_xpath)
    if helper_fn.is_element_present(text_area_xpath):
        text_area = helper_fn.find_element(text_area_xpath)
        text_area.send_keys(text)

        #send button
        send_btn_xpath = "//*[@data-testid='fruitjuice-send-button']"
        helper_fn.wait_for_element(send_btn_xpath)
        send_btn = helper_fn.find_element(send_btn_xpath)
        #time.sleep(1)
        send_btn.click()

    time.sleep(3)
    response_xpath_light = "//*[@class='markdown prose w-full break-words dark:prose-invert light']" # for light mode
    response_xpath_dark = "//*[@class='markdown prose w-full break-words dark:prose-invert dark']" # for dark mode
    regenrate_xpath = '//*[@class="absolute bottom-0 right-full top-0 -mr-3.5 hidden pr-5 pt-1 group-hover/conversation-turn:block"]'
    helper_fn.wait_for_element(regenrate_xpath,120)

    response_xpath = response_xpath_dark if helper_fn.is_element_present(response_xpath_dark) else response_xpath_light # check for dark mode or light mode
    return send(response_xpath)
    



def stop_chat_gpt():
    driver.close()
    driver.quit()

start_chat_gpt()

@app.route('/gpt', methods=['POST'])
def receive_message():
    data = request.get_json()  # JSON 데이터를 파싱합니다.
    message = data.get('message', 'No message received')  # 'message' 키를 찾고, 없으면 기본 메시지를 설정합니다.
    return jsonify({'response': make_gpt_request(message)}), 200  # 응답을 JSON 형태로 반환합니다.

if __name__ == '__main__':
    app.run(port=5001)  # 5001 포트에서 서버를 실행합니다.