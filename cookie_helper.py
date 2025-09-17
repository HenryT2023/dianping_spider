#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
from urllib.parse import urljoin

def get_basic_cookies():
    """
    获取基础的大众点评Cookie
    """
    session = requests.Session()
    
    # 模拟真实浏览器的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        print("正在尝试获取大众点评基础Cookie...")
        
        # 添加随机延迟
        time.sleep(random.uniform(1, 3))
        
        # 尝试访问大众点评首页
        response = session.get('http://www.dianping.com/', headers=headers, timeout=15, allow_redirects=True)
        
        print(f"请求状态码: {response.status_code}")
        print(f"响应URL: {response.url}")
        
        if response.status_code == 200:
            cookies = session.cookies.get_dict()
            
            if cookies:
                cookie_string = '; '.join([f"{name}={value}" for name, value in cookies.items()])
                print(f"\n成功获取到Cookie:")
                print(f"Cookie数量: {len(cookies)}")
                for name, value in cookies.items():
                    print(f"  {name}: {value}")
                
                return cookie_string
            else:
                print("响应成功但未获取到Cookie")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求异常: {str(e)}")
        return None
    except Exception as e:
        print(f"获取Cookie时发生错误: {str(e)}")
        return None

def update_config_cookie(cookie_string):
    """
    更新配置文件中的Cookie
    """
    if not cookie_string:
        print("Cookie为空，无法更新配置")
        return False
    
    try:
        config_path = '/Users/hal/Documents/GitHub/dianping_spider/config.ini'
        
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新Cookie行
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('Cookie:'):
                lines[i] = f'Cookie: {cookie_string}\n'
                updated = True
                break
        
        if updated:
            # 写回配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print("配置文件已更新")
            return True
        else:
            print("未找到Cookie配置行")
            return False
            
    except Exception as e:
        print(f"更新配置文件时出错: {str(e)}")
        return False

def main():
    """
    主函数
    """
    print("=== 大众点评Cookie获取工具 ===\n")
    
    # 获取Cookie
    cookie = get_basic_cookies()
    
    if cookie:
        print(f"\n获取到的完整Cookie字符串:")
        print(f"{cookie}\n")
        
        # 询问是否更新配置文件
        choice = input("是否将此Cookie更新到配置文件? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if update_config_cookie(cookie):
                print("✅ Cookie已成功更新到配置文件")
            else:
                print("❌ 更新配置文件失败")
        else:
            print("请手动将上述Cookie复制到config.ini文件中")
    else:
        print("❌ 未能获取到有效的Cookie")
        print("\n建议:")
        print("1. 检查网络连接")
        print("2. 手动访问 http://www.dianping.com 获取Cookie")
        print("3. 使用浏览器开发者工具复制Cookie")

if __name__ == "__main__":
    main()
