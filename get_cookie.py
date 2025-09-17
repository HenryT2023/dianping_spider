#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from urllib.parse import urljoin

def get_dianping_cookies():
    """
    获取大众点评的Cookie
    """
    session = requests.Session()
    
    # 设置User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # 访问大众点评首页
        print("正在访问大众点评首页...")
        response = session.get('https://www.dianping.com/', headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("成功访问大众点评首页")
            
            # 获取所有Cookie
            cookies = session.cookies.get_dict()
            
            if cookies:
                # 将Cookie转换为字符串格式
                cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
                
                print("获取到的Cookie:")
                print(cookie_string)
                print("\n各个Cookie详情:")
                for name, value in cookies.items():
                    print(f"  {name}: {value}")
                
                return cookie_string
            else:
                print("未获取到Cookie")
                return None
        else:
            print(f"访问失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"获取Cookie时出错: {str(e)}")
        return None

if __name__ == "__main__":
    cookie = get_dianping_cookies()
    if cookie:
        print(f"\n可用的Cookie字符串:\n{cookie}")
    else:
        print("未能获取到有效的Cookie")
