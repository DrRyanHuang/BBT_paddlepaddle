import util

from datetime import datetime

import cv2
import numpy as np



# ----- 读取配置文件 -------
filename = 'CFG'
config = util.getConfig(filename)


# ----- 读取页面宽高颜色配置 -----
page_width = config.getint('page_set', 'width')
page_height = config.getint('page_set', 'height')
page_bgcolor = config.get('page_set', 'bgcolor')
R, G, B = util.splitRGB(page_bgcolor)

background = np.tile([[[R, G, B]]], [page_height, page_width, 1]).astype(np.uint8)


# ----- 读取顶部标题的配置内容 -----
file = config.get('first_line', 'file_path')
font = config.get('first_line', 'font')
color = config.get('first_line', 'color')
size = config.getint('first_line', 'size')
top2charactor = config.getint('first_line', 'top2charactor')

with open(file, 'r') as f:
    first_line = f.read()
R, G, B = util.splitRGB(color)

w, _ = util.getCharacterSize(background, first_line, font, textSize=size)
start = (page_width - w) // 2  # 求得初始写字的位置
background = util.cv2ImgAddText(background, first_line, start, top2charactor, font, textColor=(R, G, B), textSize=size)


# ----- 读取最后一根线的配置内容 -----
line_color = config.get('last_line', 'line_color')
line_proportion = config.getfloat('last_line', 'line_proportion')
line_thickness = config.getint('last_line', 'line_thickness')
line2button = config.getint('last_line', 'line2button')
R, G, B = util.splitRGB(line_color)

start = int(0.5*(1-line_proportion)*page_width)
pt1 = start, page_height - line2button
pt2 = page_width-start, page_height - line2button

cv2.line(background, pt1, pt2, (B, G, R), line_thickness) # 绘制最后一根线


# ----- 读取最后一根线的爸爸的配置内容 -----
line2line_proportion = config.getfloat('last_line', 'line2line_proportion')
l2l_dis = int(line2line_proportion * page_height)
pt1_ba = pt1[0], pt1[1] - l2l_dis
pt2_ba = pt2[0], pt2[1] - l2l_dis
cv2.line(background, pt1_ba, pt2_ba, (B, G, R), line_thickness) # 绘制倒数第二根线


# ---------- 放置二维码 ----------
QR_code_path = config.get('last_line', 'QR_code')
QR_code = cv2.imread(QR_code_path)
h, w, _ = QR_code.shape
QR_code_proportion = config.getfloat('last_line', 'QR_code_proportion')
if h > w:
    h_new = int(page_height * QR_code_proportion)
    w_new = int(h_new/h * w)
else:
    w_new = int(page_width * QR_code_proportion)
    h_new = int(w_new/h * w)
img_size = w_new, h_new
QR_code = cv2.resize(QR_code, img_size)

QR_code_h, QR_code_w, _ = QR_code.shape
QR_top = (pt1[1] - pt1_ba[1] - QR_code_h) // 2 + pt1_ba[1]
QR_left = page_width//2 - QR_code_w//2
background[QR_top:QR_top+QR_code_h, QR_left:QR_left+QR_code_w] = QR_code # 将二维码放置


# ---------- 绘制二维码左右的直线 ----------
distance_proportion = config.getfloat('last_line', 'distance_proportion')
vertical_line_thickness = config.getint('last_line', 'vertical_line_thickness')
vertical_line_dist = int(distance_proportion*page_width)
left = QR_left - vertical_line_dist
right = QR_left + QR_code_w + vertical_line_dist
top = QR_top  # 这里偷懒了, 左右两边的虚线直接和二维码对其了
buttom = QR_top + QR_code_h

cv2.line(background, (left, top), (left, buttom), (B, G, R), vertical_line_thickness) # 绘制倒数第二根线
cv2.line(background, (right, top), (right, buttom), (B, G, R), vertical_line_thickness) # 绘制倒数第二根线


# ---------- 绘制圆圈 ----------
distance_proportion = int(config.getfloat('last_line', 'bian2yuan_distance_proportion') * page_width)
ratio = int(config.getfloat('last_line', 'ratio') * page_width)
color = config.get('last_line', 'cycle_color')
R, G, B = util.splitRGB(color)

y = (pt1_ba[1] + pt1[1]) // 2
x1 = start + distance_proportion
x2 = right + distance_proportion
cv2.circle(background, (x1, y), ratio, (B, G, R), -1)
cv2.circle(background, (x2, y), ratio, (B, G, R), -1)


# ---------- 在圆圈上写字 ----------
font_color = config.get('last_line', 'font_color')
font_file = config.get('last_line', 'font_file')
font_size = config.getint('last_line', 'font_size')
R, G, B = util.splitRGB(page_bgcolor)

w, h = util.getCharacterSize(background, '宜', font_file, textSize=font_size)
background = util.cv2ImgAddText(background, '宜', x1-w//2, y-h//2, font, textColor=(R, G, B), textSize=font_size)
w, h = util.getCharacterSize(background, '忌', font_file, textSize=font_size)
background = util.cv2ImgAddText(background, '忌', x2-w//2, y-h//2, font, textColor=(R, G, B), textSize=font_size)


# ---------- 写宜和忌 ----------
yiji_font_color = config.get('last_line', 'yiji_font_color')
yiji_font_file = config.get('last_line', 'yiji_font_file')
yiji_font_size = config.getint('last_line', 'yiji_font_size')
yiji_shift = int(config.getfloat('last_line', 'yiji_cir_cen_shift') * page_width)
R, G, B = util.splitRGB(yiji_font_color)

w, h = util.getCharacterSize(background, '早点\n睡觉', font_file, textSize=font_size)
background = util.cv2ImgAddText(background, '早点\n睡觉', x1+yiji_shift-w//2, y-h//2, font, textColor=(R, G, B), textSize=yiji_font_size)
w, h = util.getCharacterSize(background, '又吃\n夜宵', font_file, textSize=font_size)
background = util.cv2ImgAddText(background, '又吃\n夜宵', x2+yiji_shift-w//2, y-h//2, font, textColor=(R, G, B), textSize=yiji_font_size)



# ---------- 写日期等 ----------
date = config.get('date', 'date')
date_day_font = config.get('date', 'date_day_font')
date_proportion = config.getfloat('date', 'date_proportion')
date_day_size = config.getint('date', 'date_day_size')
date_day_color = config.get('date', 'date_day_color')
R, G, B = util.splitRGB(date_day_color)

cday = datetime.strptime(date, '%Y-%m-%d')

left_time_str = cday.strftime('%b.%Y') # %a %b.%Y
middle_day_str = cday.strftime('%d')
#right_str = 

# 写中间的日期
w, h = util.getCharacterSize(background, middle_day_str, date_day_font, textSize=date_day_size)
date_y = int(date_proportion * page_height)
background = util.cv2ImgAddText(background, 
                                middle_day_str, 
                                int(0.5*page_width)-w//2, 
                                date_y-h//2, 
                                date_day_font, 
                                textColor=(R, G, B), 
                                textSize=date_day_size)


year_month_font = config.get('date', 'year_month_font')
year_month_shife = config.getfloat('date', 'year_month_shife')
year_month_size = config.getint('date', 'year_month_size')
year_month_color = config.get('date', 'year_month_color')
year_month_y_shift = config.getint('date', 'year_month_y_shift')


# 写左边的日期
w, h = util.getCharacterSize(background, left_time_str, year_month_font, textSize=year_month_size)
date_x_shift = int(year_month_shife * page_width)

background = util.cv2ImgAddText(background, 
                                left_time_str, 
                                int(0.5*page_width)-w//2-date_x_shift, 
                                date_y-h//2+year_month_y_shift, 
                                year_month_font, 
                                textColor=(R, G, B), 
                                textSize=year_month_size)



right_chara_font = config.get('date', 'right_chara_font')
right_chara_shift = int(config.getfloat('date', 'right_chara_shife') * page_width)
right_chara_size = config.getint('date', 'right_chara_size')
right_chara_color = config.get('date', 'right_chara_color')
right_chara_y_shift = config.getint('date', 'right_chara_y_shift')
right_descr_file = config.get('date', 'right_chara_content')
with open(right_descr_file) as f:
    right_content = f.read()

R, G, B = util.splitRGB(right_chara_color)

# 写右边儿的预告
background = util.preformCenteredWord(background, 
                                      right_chara_shift+page_width//2, 
                                      date_y+right_chara_y_shift, 
                                      right_content.format(2), 
                                      (R, G, B), 
                                      right_chara_font, 
                                      right_chara_size)

# ---------- 写鸡汤 ----------
jitang_center_x = int(config.getfloat('jitang', 'jitang_center_x') * page_width)
jitang_center_y = int(config.getfloat('jitang', 'jitang_center_y') * page_height)
jitang_path = config.get('jitang', 'jitang_content')
jitang_size = config.getint('jitang', 'jitang_size')
jitang_font = config.get('jitang', 'jitang_font')
jitang_color = config.get('jitang', 'jitang_color')

with open(jitang_path) as f:
    jitang_content = f.read()
R, G, B = util.splitRGB(jitang_color)

background = util.preformCenteredWord(background, 
                                      jitang_center_x, 
                                      jitang_center_y, 
                                      jitang_content, 
                                      (R, G, B), 
                                      jitang_font, 
                                      jitang_size)

# ---------- 放置表情包 ----------
bqb_path = config.get('biaoqingbao', 'bqb_path')
bqb_img = cv2.imread(bqb_path)

bqb_center_x = int(config.getfloat('biaoqingbao', 'bqb_center_x') * page_width)
bqb_center_y = int(config.getfloat('biaoqingbao', 'bqb_center_y') * page_height)
max_width = int(config.getfloat('biaoqingbao', 'max_width') * page_width)
max_height = int(config.getfloat('biaoqingbao', 'max_height') * page_height)

background = util.putImgToBackGr(bqb_img, background, bqb_center_x, bqb_center_y, max_width, max_height)

cv2.imwrite('output.png', background)





int(0.5*page_width)-w//2, date_y-h//2








