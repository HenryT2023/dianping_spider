#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def update_cookie_in_config(cookie_string):
    """
    更新配置文件中的Cookie
    """
    config_path = '/Users/hal/Documents/GitHub/dianping_spider/config.ini'
    
    try:
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新Cookie行
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('Cookie:'):
                lines[i] = f'Cookie: {cookie_string.strip()}\n'
                updated = True
                break
        
        if updated:
            # 写回配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        else:
            print("❌ 未找到Cookie配置行")
            return False
            
    except Exception as e:
        print(f"❌ 更新配置文件时出错: {str(e)}")
        return False

def main():
    """
    主函数 - 手动输入Cookie
    """
    print("=== 大众点评Cookie手动输入工具 ===\n")
    print("请按照以下步骤获取Cookie:")
    print("1. 打开浏览器访问 https://www.dianping.com")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Network标签页")
    print("4. 刷新页面")
    print("5. 点击第一个请求，在Request Headers中找到Cookie")
    print("6. 复制完整的Cookie值\n")
    
    print("或者使用控制台方法:")
    print("1. 在开发者工具中切换到Console标签")
    print("2. 输入: document.cookie")
    print("3. 复制返回的Cookie字符串\n")
    
    # 获取用户输入的Cookie
    cookie_input = input("请粘贴Cookie字符串 (输入'q'退出): ").strip()
    
    if cookie_input.lower() == 'q':
        print("退出程序")
        return
    
    if not cookie_input:
        print("❌ Cookie不能为空")
        return
    
    # 验证Cookie格式
    if '=' not in cookie_input:
        print("❌ Cookie格式不正确，应该包含键值对")
        return
    
    # 更新配置文件
    if update_cookie_in_config(cookie_input):
        print("✅ Cookie已成功更新到配置文件")
        print(f"更新的Cookie: {cookie_input[:100]}..." if len(cookie_input) > 100 else f"更新的Cookie: {cookie_input}")
        
        # 询问是否立即测试
        test_choice = input("\n是否立即测试爬虫? (y/n): ").lower().strip()
        if test_choice in ['y', 'yes', '是']:
            print("正在启动爬虫测试...")
            os.system("conda activate dianping_spider && python main.py --normal 1")
    else:
        print("❌ 更新配置文件失败")

if __name__ == "__main__":
    main()
