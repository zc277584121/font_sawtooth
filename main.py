from flask import Flask

app = Flask(__name__)

from PIL import ImageGrab
from selenium import webdriver
import time
import threading
import os
# from wsgiref.simple_server import make_server
import random
import letters_and_chinese_keys
import numpy as np
import cv2 as cv

port = 5000

screen_shot_save_img_dir = "D:\\project\\font_sawtooth\\screenshot_imgs"
res_img_dir = 'D:\\project\\font_sawtooth\\res_imgs'

url = 'http://127.0.0.1:' + str(port) + '/'
driver = webdriver.Chrome()
driver.maximize_window()
driver.get(url)

if not os.path.exists(screen_shot_save_img_dir):
    os.mkdir(screen_shot_save_img_dir)
if not os.path.exists(res_img_dir):
    os.mkdir(res_img_dir)

font_size = '1'
global_all_text_line = ''




def generate_text_color():
    r = hex(random.randint(0, 255))[2:]
    g = hex(random.randint(0, 255))[2:]
    b = hex(random.randint(0, 255))[2:]
    if len(r) == 1:
        r = '0' + r
    if len(g) == 1:
        g = '0' + g
    if len(b) == 1:
        b = '0' + b
    return r, g, b


def generate_bg_color(text_r, text_g, text_b):
    min_diff = 90

    text_r = int(('0x' + text_r), 16)
    text_g = int(('0x' + text_g), 16)
    text_b = int(('0x' + text_b), 16)

    min_r = text_r - min_diff
    min_r = max(0, min_r)
    max_r = text_r + min_diff
    max_r = min(255, max_r)

    min_g = text_g - min_diff
    min_g = max(0, min_g)
    max_g = text_g + min_diff
    max_g = min(255, max_g)

    min_b = text_b - min_diff
    min_b = max(0, min_b)
    max_b = text_b + min_diff
    max_b = min(255, max_b)

    bg_r = hex(random.choice(list(range(0, min_r)) + list(range(max_r, 255))))[2:]
    bg_g = hex(random.choice(list(range(0, min_g)) + list(range(max_g, 255))))[2:]
    bg_b = hex(random.choice(list(range(0, min_b)) + list(range(max_b, 255))))[2:]
    if random.random() < 0.2:
        bg_r, bg_g, bg_b = 'ff', 'ff', 'ff'
    if len(bg_r) == 1:
        bg_r = '0' + bg_r
    if len(bg_g) == 1:
        bg_g = '0' + bg_g
    if len(bg_b) == 1:
        bg_b = '0' + bg_b
    return bg_r, bg_g, bg_b


def text_img_random_change(text_img):
    interpolation_method = random.choice([cv.INTER_NEAREST, cv.INTER_LINEAR, cv.INTER_CUBIC])
    bg_color0 = text_img[2, 2]
    r = int(bg_color0[2])
    g = int(bg_color0[1])
    b = int(bg_color0[0])

    h, w = text_img.shape[:2]
    padding = h
    text_bg_img = np.zeros(shape=(h + 2 * padding, w + 2 * padding, 3), dtype=np.uint8)
    cv.rectangle(text_bg_img, (0, 0), (w + 2 * padding, h + 2 * padding), (b, g, r), -1)
    bg_h, bg_w = text_bg_img.shape[:2]
    text_bg_img[padding: h + padding, padding: w + padding, :] = text_img
    center = (bg_w / 2, bg_h / 2)
    angle = random.randint(-3, 3)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    padding_rotated = cv.warpAffine(text_bg_img, M, (bg_w, bg_h), flags=interpolation_method)
    # element = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    # if random.random() < 0.2:
    #     padding_rotated = cv.erode(padding_rotated, element)
    # if random.random() > 0.8:
    #     padding_rotated = cv.dilate(padding_rotated, element)
    rotated_text_img = padding_rotated[padding: h + padding, padding: w + padding, :]
    rotated_text_img = cv.cvtColor(rotated_text_img, cv.COLOR_BGR2GRAY)
    resized_img = cv.resize(rotated_text_img, dsize=(280, 32))
    return resized_img


letters_and_num = letters_and_chinese_keys.alphabet[:36]
chinese = letters_and_chinese_keys.alphabet[36:]

col_num = 10
row_num = 40
label_length = 8

height_width_rate = 32 / 280
screen_shot_top_y = 123
screen_shot_bottom_y = 1039
# screen_shot_
font_size_map_line_height = {  # img_w = line_height / height_width_rate
    1: 14,
    2: 15,
    3: 18,
    4: 21
}
font_size_map_chinese_width = {
    1: 12,
    2: 13,
    3: 16,
    4: 18
}

bg_color = '#ffffff'


class WebShow(threading.Thread):
    def run(self):
        app.run(debug=False)

total_img_num = 1000
total_img_index = 0
mid_dir_img_num = 1000
label_txt_path = 'D:\\project\\font_sawtooth\\labels.txt'

class ScreenShot(threading.Thread):
    def run(self):
        shot_times = 999999
        with open(label_txt_path, 'w', encoding='utf-8') as f:
            for shot_index in range(shot_times):

                driver.refresh()
                time.sleep(0.5)  # 网页刷新要在显示器上的反应一段时间，后面再截屏，以保证截下的是刷新后的
                clip = ImageGrab.grab((7, screen_shot_top_y, 1920, screen_shot_bottom_y))
                # time.sleep(0.8)
                if clip is not None:
                    screen_shot_img_path = os.path.join(screen_shot_save_img_dir, str(shot_index) + '.bmp')
                    clip.save(screen_shot_img_path)
                    img = cv.imread(screen_shot_img_path)
                    table_x = np.array(list(range(col_num)))
                    table_y = np.array(list(range(row_num)))
                    global font_size, font_size_map_line_height, font_size_map_chinese_width
                    print(font_size)
                    # print(font_size_map_line_height)
                    lint_height = font_size_map_line_height[int(font_size)]
                    chinese_width = font_size_map_chinese_width[int(font_size)]
                    table_x = table_x * (label_length + 2) * chinese_width - (
                            lint_height / height_width_rate / 2 - (
                            label_length + 2) * chinese_width / 2)
                    table_y = table_y * lint_height
                    global global_all_text_line
                    text_list_list = []
                    text_list = global_all_text_line.split('<br />')
                    for text_line in text_list:
                        temp_list = text_line.split('&nbsp')
                        one_line_list = []
                        for temp in temp_list:
                            if temp != '':
                                one_line_list.append(temp)
                        text_list_list.append(one_line_list)
                    # print('len(table_y):', len(table_y))
                    # print('len(table_x):', len(table_x))

                    for i, x in enumerate(table_x):
                        for j, y in enumerate(table_y):
                            x = int(max(0, x))
                            y = int(y)
                            text_img = img[y: y + lint_height, x: x + int(lint_height / height_width_rate)]
                            if 0 in text_img.shape[:2]:
                                # print('error')
                                continue
                            changed_text_img = text_img_random_change(text_img)
                            global total_img_index, total_img_num
                            res_mid_dir = os.path.join(res_img_dir, str(total_img_index // mid_dir_img_num))
                            if not os.path.exists(res_mid_dir):
                                os.mkdir(res_mid_dir)
                            res_img_path = os.path.join(res_mid_dir, str(total_img_index).zfill(6) + random.choice(['.bmp', '.jpg']))
                            cv.imwrite(res_img_path,changed_text_img)

                            f.write(os.path.join(str(total_img_index // mid_dir_img_num ), os.path.split(res_img_path)[-1]))
                            f.write('\t')
                            f.write(text_list_list[j][i])
                            f.write('\n')
                            total_img_index += 1
                            if total_img_index >= total_img_num:
                                return
                            # with open(os.path.join(screen_shot_save_img_dir, str(shot_index) + '_' + str(x) + '_' + str(y) + '.txt'),
                            #           'w',
                            #           encoding='utf-8') as f:
                            #     f.write(text_list_list[j][i])


@app.route('/')
def index():
    font = random.choice(['宋体', '黑体'])
    if font is '宋体':
        space = '&nbsp'
    else:
        space = '&nbsp' * 2
    # text = random.choice(['请选择转自动业务流程\t请选择转自动业务流ab\t请选择转自动业务abcd\t请选择转自动业abcabm\t请选择转自动abcdabmm\t选择转自动abcdabiiij\t'])
    # text = space + letters_and_num[:label_length * 2] + 2 * space + chinese[:label_length] + space
    all_text_line = ''
    for i in range(row_num):
        text_line = ''
        for j in range(col_num):
            text = ''
            for k in range(label_length):
                character = random.choice(letters_and_chinese_keys.alphabet)
                if character in letters_and_num:
                    character += random.choice(letters_and_num)
                text += character
            text = space + text + space
            text_line += text
        text_line += '<br />'
        all_text_line += text_line

    global global_all_text_line
    global_all_text_line = all_text_line
    # text = (text * 4 + '<br />') * 128
    # color = 'rgb(' + str(random.randint(0, 255)) + ',' + str(random.randint(0, 100)) + ',' + str(random.randint(0, 100)) + ')'
    # color = 'rgb(255, 255, 255)'
    text_r, text_g, text_b = generate_text_color()
    # color = '#ff0000'
    text_color = '#' + text_r + text_g + text_b
    # print('text_color: ', text_color)
    bg_r, bg_g, bg_b = generate_bg_color(text_r, text_g, text_b)
    global bg_color
    bg_color = '#' + bg_r + bg_g + bg_b
    # font = random.choice(['宋体', '黑体', '微软雅黑', '仿宋', '新宋体', '华文行楷', '华文新魏'])
    global font_size
    font_size = str(random.randint(1, 4))
    # print('font_size_0:', font_size)
    web_content = '<body bgcolor="' + bg_color + '"><p style="font-family:' + font + '"><font size="' + font_size + '" color=' + text_color + '>' + global_all_text_line + '</font></p></body>'
    # global change_flag
    return web_content


if __name__ == '__main__':
    web_show_thread = WebShow()
    web_show_thread.start()
    time.sleep(0.8)  # 服务启动有个反应时间,启动后才可以刷新截出网页
    screen_shot_thread = ScreenShot()
    screen_shot_thread.start()
    # print(655)
    # app.
