#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北京时间工具函数
提供统一的北京时区时间处理
"""

from datetime import datetime, timezone, timedelta


def get_beijing_time():
    """获取北京时间（datetime对象）"""
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(timezone.utc).astimezone(beijing_tz)


def get_beijing_now_str(format_str='%Y-%m-%d %H:%M:%S'):
    """获取北京时间字符串"""
    return get_beijing_time().strftime(format_str)


def get_beijing_date_str(format_str='%Y%m%d'):
    """获取北京日期字符串"""
    return get_beijing_time().strftime(format_str)


def get_beijing_datetime_str():
    """获取北京日期时间字符串（适用于文件名）"""
    return get_beijing_time().strftime('%Y%m%d%H%M%S')


# 兼容旧代码的函数名
def beijing_now():
    """别名：获取北京时间"""
    return get_beijing_time()
