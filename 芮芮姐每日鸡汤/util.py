# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 16:27:22 2020

@author: RyanHuang
"""
import cv2
import configparser
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def getConfig(filename, encoding='utf-8'):
    '''
    @Brife:
        获取配置文件
    @Param:
        filename : 文件路径(名字)
        encoding : 文件编码
    '''
    # 生成ConfigParser对象
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(filename, encoding=encoding)
    
    return config



def splitRGB(color_str):
    '''
    @Brife:
        将形如 '0xFFEEAA' 的字符串分成三通道
    @Param:
        color_str : 形如'0xFFEEAA'
    '''
    color = int(color_str, 16)

    R = color >> 16
    G = (color % 0x10000) >> 8
    B = color % 0x100
    
    return R, G, B



def cv2ImgAddText(img, text, left, top, font_file, textColor=(0, 255, 0), textSize=20):
    '''
    @Brife:
        
    @Param:
        font_file : 字体文件路径
    @Notice:
        摘自博客：https://blog.csdn.net/ctwy291314/article/details/91492048
    '''
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        font_file, textSize, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)



def getCharacterSize(img, text, font_file, textSize):
    '''
    @Brife:
        通过PIL来获取汉字字符串的大小
    '''
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        font_file, textSize, encoding="utf-8")
    
    w, h = draw.textsize(text, fontStyle)
    return w, h
    
    

def preformCenteredWord(img, center_x, center_y, text, textColor, font_file, textSize):
    '''
    @Brife:
        给定画板, 给定中心等, 将句子放在中心
        用 `\n` 来划分句子
    @Param:
        text : 多行句子用 `\n` 连接就好
    '''
    w_all, h_all = getCharacterSize(img, text, font_file, textSize)
    left, top = center_x-w_all//2, center_y-h_all//2
    text_list = text.split('\n')
    for sen in text_list:
        w_sen, h_sen = getCharacterSize(img, sen, font_file, textSize)
        y = top
        x = left + (w_all - w_sen)//2
        img = cv2ImgAddText(img, sen, x, y, font_file, textColor=textColor, textSize=textSize)
        top += h_sen
        
    return img



def putImgToBackGr(img, background, center_x, center_y, max_w, max_h):
    '''
    @Brfie:
        将给定图片放在背景图片上
    '''
    img_h, img_w, _ = img.shape

    if (img_h <= max_h) and (img_w <= max_w):
        pass
    elif max_w/max_h >= img_w/img_h:
        img = cv2.resize(img, (int(max_h/img_h*img_w), max_h))
    else:
        img = cv2.resize(img, (max_w, int(max_w/img_w*max_h)))
    img_h, img_w, _ = img.shape
    
    x_start = center_x - img_w//2
    y_start = center_y - img_h//2
    background[y_start:y_start+img_h, x_start:x_start+img_w] = img
    
    return background


