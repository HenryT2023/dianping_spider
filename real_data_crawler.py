#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import json
import re
from bs4 import BeautifulSoup
import pymongo
from urllib.parse import quote
import configparser
from datetime import datetime

class RealDianpingCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.load_config()
        self.setup_mongodb()
        
    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        # 获取Cookie
        self.cookies_str = config.get('requests', 'cookie', fallback='')
        self.cookies = self.parse_cookies(self.cookies_str)
        
        # 获取其他配置
        self.user_agent = config.get('requests', 'user_agent', fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        print(f"Cookie状态: {'已配置' if self.cookies else '未配置'}")
        
    def parse_cookies(self, cookie_str):
        """解析Cookie字符串"""
        if not cookie_str:
            return {}
        
        cookies = {}
        for item in cookie_str.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        return cookies
    
    def setup_mongodb(self):
        """设置MongoDB连接"""
        try:
            self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
            self.db = self.mongo_client['dianping']
            self.restaurants_collection = self.db['real_restaurants']
            self.reviews_collection = self.db['real_reviews']
            print("✅ MongoDB连接成功")
        except Exception as e:
            print(f"❌ MongoDB连接失败: {e}")
            self.mongo_client = None
    
    def get_headers(self):
        """获取请求头"""
        return {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.dianping.com/',
            'DNT': '1',
        }
    
    def test_connection(self):
        """测试连接和Cookie有效性"""
        print("🔍 测试大众点评连接...")
        
        test_urls = [
            'https://www.dianping.com/',
            'https://www.dianping.com/dalian',
            'http://www.dianping.com/dalian/ch10'
        ]
        
        for url in test_urls:
            try:
                print(f"测试URL: {url}")
                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    cookies=self.cookies,
                    timeout=10,
                    allow_redirects=True
                )
                
                print(f"状态码: {response.status_code}")
                print(f"最终URL: {response.url}")
                print(f"内容长度: {len(response.text)}")
                
                # 检查是否成功
                if response.status_code == 200:
                    if 'verify' in response.url or 'login' in response.url:
                        print("⚠️ 被重定向到验证/登录页面")
                    elif '大众点评' in response.text or 'dianping' in response.text.lower():
                        print("✅ 连接成功！")
                        return True
                    else:
                        print("⚠️ 页面内容异常")
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 连接错误: {e}")
        
        return False
    
    def manual_cookie_update(self):
        """手动更新Cookie"""
        print("\n" + "="*60)
        print("🍪 手动Cookie更新指南")
        print("="*60)
        print("1. 打开浏览器，访问 https://www.dianping.com/dalian")
        print("2. 登录你的大众点评账号")
        print("3. 按F12打开开发者工具")
        print("4. 切换到Network标签")
        print("5. 刷新页面")
        print("6. 找到第一个请求，右键 -> Copy -> Copy as cURL")
        print("7. 从cURL中提取Cookie部分")
        print("\n请输入新的Cookie (直接粘贴完整的Cookie字符串):")
        
        new_cookie = input().strip()
        
        if new_cookie:
            # 更新配置文件
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            config.set('requests', 'cookie', new_cookie)
            
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            # 重新加载配置
            self.load_config()
            print("✅ Cookie已更新！")
            
            # 测试新Cookie
            if self.test_connection():
                return True
        
        return False
    
    def try_different_strategies(self):
        """尝试不同的爬取策略"""
        print("\n🚀 尝试不同的爬取策略...")
        
        strategies = [
            {
                'name': '策略1: 直接访问餐厅列表',
                'urls': [
                    'https://www.dianping.com/dalian/ch10/g110',
                    'https://www.dianping.com/dalian/ch10',
                ]
            },
            {
                'name': '策略2: 搜索接口',
                'urls': [
                    'https://www.dianping.com/search/keyword/8/10_自助餐',
                    'https://www.dianping.com/dalian/search/category/10/10/g110',
                ]
            },
            {
                'name': '策略3: AJAX接口',
                'urls': [
                    'https://www.dianping.com/ajax/json/shop/category/shoplist',
                    'https://www.dianping.com/ajax/json/search/searchshop',
                ]
            }
        ]
        
        for strategy in strategies:
            print(f"\n🔄 {strategy['name']}")
            
            for url in strategy['urls']:
                try:
                    print(f"尝试: {url}")
                    
                    # 随机延迟
                    time.sleep(random.uniform(3, 8))
                    
                    response = self.session.get(
                        url,
                        headers=self.get_headers(),
                        cookies=self.cookies,
                        timeout=15,
                        allow_redirects=True
                    )
                    
                    print(f"状态: {response.status_code} | URL: {response.url}")
                    
                    if response.status_code == 200 and 'verify' not in response.url:
                        # 保存页面用于分析
                        filename = f"page_{int(time.time())}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        print(f"✅ 成功获取页面，已保存为 {filename}")
                        
                        # 尝试解析数据
                        restaurants = self.parse_page(response.text)
                        if restaurants:
                            print(f"🎉 解析到 {len(restaurants)} 个餐厅！")
                            self.save_restaurants(restaurants)
                            return restaurants
                    
                except Exception as e:
                    print(f"❌ 请求失败: {e}")
        
        return []
    
    def parse_page(self, html_content):
        """解析页面内容"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            restaurants = []
            
            # 多种解析策略
            selectors = [
                '.shop-list .shop-item',
                '.shoplist .shopitem',
                '.shop-wrap',
                '.list-item',
                '[data-shopid]',
                '.shop-info',
                '.poi-item'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"使用选择器 {selector} 找到 {len(items)} 个项目")
                    
                    for item in items:
                        restaurant = self.extract_restaurant_info(item)
                        if restaurant:
                            restaurants.append(restaurant)
                    
                    if restaurants:
                        break
            
            # 如果HTML解析失败，尝试JSON数据
            if not restaurants:
                restaurants = self.extract_json_data(html_content)
            
            return restaurants
            
        except Exception as e:
            print(f"解析页面时出错: {e}")
            return []
    
    def extract_restaurant_info(self, item):
        """提取餐厅信息"""
        try:
            restaurant = {}
            
            # 餐厅名称
            name_elem = item.select_one('.shop-name, .shopname, h3, .title, a[title]')
            if name_elem:
                restaurant['name'] = name_elem.get_text(strip=True)
            
            # 评分
            rating_elem = item.select_one('.shop-star, .star, .rating, .score')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    restaurant['rating'] = float(rating_match.group(1))
            
            # 地址
            addr_elem = item.select_one('.shop-addr, .address, .addr')
            if addr_elem:
                restaurant['address'] = addr_elem.get_text(strip=True)
            
            # 价格
            price_elem = item.select_one('.shop-price, .price, .avgprice')
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'(\d+)', price_text)
                if price_match:
                    restaurant['price_per_person'] = int(price_match.group(1))
            
            # 店铺ID
            shop_id = item.get('data-shopid') or item.get('data-id')
            if shop_id:
                restaurant['shop_id'] = shop_id
            
            # 添加爬取时间
            restaurant['crawl_time'] = datetime.now()
            restaurant['data_source'] = 'real_crawl'
            
            return restaurant if restaurant.get('name') else None
            
        except Exception as e:
            print(f"提取餐厅信息时出错: {e}")
            return None
    
    def extract_json_data(self, html_content):
        """从页面JSON数据中提取"""
        try:
            # 查找JSON数据
            json_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                r'window\.pageConfig\s*=\s*({.+?});',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches[0])
                        restaurants = self.parse_json_restaurants(data)
                        if restaurants:
                            print(f"从JSON提取到 {len(restaurants)} 个餐厅")
                            return restaurants
                    except:
                        continue
            
            return []
            
        except Exception as e:
            print(f"提取JSON数据时出错: {e}")
            return []
    
    def parse_json_restaurants(self, data):
        """解析JSON中的餐厅数据"""
        restaurants = []
        
        def find_restaurants(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['shops', 'list', 'data', 'results', 'items']:
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and 'name' in item:
                                    restaurant = {
                                        'name': item.get('name', ''),
                                        'shop_id': item.get('id', item.get('shopId', '')),
                                        'rating': item.get('rating', item.get('avgRating', 0)),
                                        'address': item.get('address', ''),
                                        'category': item.get('category', ''),
                                        'price_per_person': item.get('avgPrice', 0),
                                        'review_count': item.get('reviewCount', 0),
                                        'crawl_time': datetime.now(),
                                        'data_source': 'real_crawl'
                                    }
                                    restaurants.append(restaurant)
                    else:
                        find_restaurants(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_restaurants(item)
        
        find_restaurants(data)
        return restaurants
    
    def save_restaurants(self, restaurants):
        """保存餐厅数据"""
        if not self.mongo_client or not restaurants:
            return
        
        try:
            # 清空旧数据
            self.restaurants_collection.delete_many({'data_source': 'real_crawl'})
            
            # 插入新数据
            result = self.restaurants_collection.insert_many(restaurants)
            print(f"✅ 成功保存 {len(result.inserted_ids)} 条真实餐厅数据")
            
            # 显示数据
            self.display_restaurants()
            
        except Exception as e:
            print(f"❌ 保存数据时出错: {e}")
    
    def display_restaurants(self):
        """显示餐厅数据"""
        print("\n" + "="*60)
        print("🎉 真实大众点评餐厅数据")
        print("="*60)
        
        restaurants = list(self.restaurants_collection.find({'data_source': 'real_crawl'}).limit(10))
        
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\n{i}. {restaurant.get('name', 'N/A')}")
            if restaurant.get('rating'):
                print(f"   评分: {restaurant['rating']} ⭐")
            if restaurant.get('address'):
                print(f"   地址: {restaurant['address']}")
            if restaurant.get('price_per_person'):
                print(f"   人均: ¥{restaurant['price_per_person']}")
            if restaurant.get('category'):
                print(f"   类型: {restaurant['category']}")
    
    def run(self):
        """运行爬虫"""
        print("=== 真实大众点评数据爬虫 ===\n")
        
        # 检查Cookie配置
        if not self.cookies:
            print("⚠️ 未检测到Cookie配置")
            if input("是否需要手动更新Cookie? (y/n): ").lower() == 'y':
                if not self.manual_cookie_update():
                    print("❌ Cookie更新失败，无法继续")
                    return
        
        # 测试连接
        if not self.test_connection():
            print("❌ 连接测试失败")
            if input("是否需要更新Cookie? (y/n): ").lower() == 'y':
                if not self.manual_cookie_update():
                    print("❌ 无法建立有效连接")
                    return
        
        # 开始爬取
        restaurants = self.try_different_strategies()
        
        if restaurants:
            print(f"\n🎉 成功获取 {len(restaurants)} 条真实数据！")
        else:
            print("\n😞 暂时无法获取真实数据")
            print("建议:")
            print("1. 确保网络连接正常")
            print("2. 更新Cookie配置")
            print("3. 尝试使用代理服务")

if __name__ == "__main__":
    crawler = RealDianpingCrawler()
    crawler.run()
