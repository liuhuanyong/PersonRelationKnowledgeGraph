#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: chenhe<hee0624@163.com>
# time: 2017-11-30
# version: 1.0

from collections import Counter
import jieba.posseg as pseg
import re


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= '\u4e00' and uchar <= '\u9fa5':
        return True
    else:
        return False

def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

def is_legal(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return False
    else:
        return True

def count_pos(str):
    """返回词性个数"""
    pos_set = set()
    words = pseg.cut(str)
    for word, flag in words:
        pos_set.add(flag)
    return len(pos_set)

def is_longsent(str):
    """根据字符串汉字长度判断是否是标题"""
    length = 0
    for uchar in str:
        if is_chinese(uchar):
            length += 1
        else:
            pass
    if length > 8:
        return True
    else:
        return False

def clear_title(title_str):
    seg_set = set(['\\', '\|', '/', '_'])
    c = Counter()
    for item in title_str:
        if item in seg_set:
            c[item] += 1
    if c.most_common(1):
        seg, count = c.most_common(1)[0]
    else:
        seg, count = '', 0
    if seg:
        title = title_str.split(seg)[0]
    else:
        title = title_str

    title = title.replace('——', '-')
    tmp = title.split('-')
    is_continue = True
    while is_continue:
        if len(tmp) > 1:
            top = tmp[-1]
            pos_num = count_pos(top)
            if pos_num > 2:
                is_continue = False
            else:
                tmp.pop()
        else:
            is_continue = False
    title = '-'.join(tmp).replace("\t", '')
    return title

def clear_pan(str):
    num = str.count('>')
    if num >= 2:
        return str.split('>')[-1]
    else:
        return str

def drop_null(arg):
    if isinstance(arg, str):
        arg = re.sub('\s', '', arg, flags=re.S)
        return arg
    elif isinstance(arg, list):
        new_list = []
        for i in arg:
            i = i.strip()
            if i:
                new_list.append(i)
            else:
                continue
        return new_list
    else:
        return arg

def drop_mutil_br(str):
    str = re.sub(r'<br>|</br>', '\n', str)
    str = re.sub(r'\n\s+', '\n', str)
    return str


def drop_mutil_blank(str):
    str = re.sub(r'\s{2,}', ' ', str)
    return str