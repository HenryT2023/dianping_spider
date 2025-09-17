#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import json
import re
from bs4 import BeautifulSoup
import pymongo
from urllib.parse import urljoin, quote
import base64

class AdvancedDianpingCrawler:
    def __init__(self):
        self.session = requests.Session()
        
        # 预定义的User-Agent列表
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        # 更新的Cookie配置
        self.cookies = {
            '_hc.v': 'e8c70e5d-fb22-43af-2857-ffe83d9f7329.1758043300',
            '_lxsdk': '199538be002c8-0b02bd0c8c3bd3-16525636-708000-199538be002c8',
            '_lxsdk_cuid': '199538be002c8-0b02bd0c8c3bd3-16525636-708000-199538be002c8',
            '_lxsdk_s': '19955ae6eca-ef3-b42-2c7%7C%7C24',
            'fspop': 'test',
            'logan_session_token': 'm0iywvv5uwdsy0t9q92o',
            # 添加更多必要的Cookie
            'cy': '8',  # 城市代码
            'cye': 'dalian',  # 城市名
        }
        
        # MongoDB连接
        try:
            self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
            self.db = self.mongo_client['dianping']
            self.restaurants_collection = self.db['real_restaurants']
            self.reviews_collection = self.db['real_reviews']
            print("✅ MongoDB连接成功")
        except Exception as e:
            print(f"❌ MongoDB连接失败: {e}")
            self.mongo_client = None
    
    def get_random_headers(self):
        """生成随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }
    
    def smart_request(self, url, max_retries=3):
        """智能请求方法"""
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers()
                
                # 随机延迟
                delay = random.uniform(8, 15)
                print(f"等待 {delay:.1f} 秒...")
                time.sleep(delay)
                
                print(f"正在请求: {url} (尝试 {attempt + 1}/{max_retries})")
                
                response = self.session.get(
                    url,
                    headers=headers,
                    cookies=self.cookies,
                    timeout=20,
                    allow_redirects=True
                )
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应URL: {response.url}")
                print(f"内容长度: {len(response.text)}")
                
                # 检查是否被重定向到验证页面
                if 'verify' in response.url or 'login' in response.url:
                    print("⚠️ 遇到验证页面，尝试其他策略...")
                    continue
                
                if response.status_code == 200:
                    return response
                    
            except Exception as e:
                print(f"请求异常: {e}")
                
            if attempt < max_retries - 1:
                wait_time = random.uniform(15, 30)
                print(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
        
        return None
    
    def try_mobile_api(self, keyword="自助餐", city_id=8):
        """尝试移动端API"""
        mobile_urls = [
            f"https://m.dianping.com/search/keyword/{city_id}/0_{quote(keyword)}",
            f"https://m.dianping.com/{city_id}/food",
            f"https://m.dianping.com/dalian/food/buffet",
        ]
        
        for url in mobile_urls:
            print(f"\n🔄 尝试移动端URL: {url}")
            
            # 模拟移动端请求头
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            try:
                response = self.session.get(
                    url,
                    headers=mobile_headers,
                    cookies=self.cookies,
                    timeout=15
                )
                
                if response.status_code == 200 and 'verify' not in response.url:
                    print(f"✅ 移动端请求成功")
                    return response
                    
            except Exception as e:
                print(f"移动端请求失败: {e}")
        
        return None
    
    def parse_restaurant_list(self, html_content):
        """解析餐厅列表"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            restaurants = []
            
            # 多种选择器策略
            selectors = [
                '.shop-list .shop-item',
                '.shoplist .shopitem', 
                '.shop-wrap',
                '.list-item',
                '[data-shopid]',
                '.shop-info',
                '.poi-item',
                '.shop-card'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"找到 {len(items)} 个餐厅项目 (选择器: {selector})")
                    
                    for item in items:
                        restaurant = self.extract_restaurant_info(item)
                        if restaurant:
                            restaurants.append(restaurant)
                    
                    if restaurants:
                        break
            
            # 如果没找到，尝试从JSON数据中提取
            if not restaurants:
                restaurants = self.extract_from_json(html_content)
            
            return restaurants
            
        except Exception as e:
            print(f"解析餐厅列表时出错: {e}")
            return []
    
    def extract_from_json(self, html_content):
        """从页面JSON数据中提取信息"""
        try:
            # 查找页面中的JSON数据
            json_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                r'window\.pageConfig\s*=\s*({.+?});',
                r'__INITIAL_DATA__\s*=\s*({.+?});'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                if matches:
                    try:
                        data = json.loads(matches[0])
                        restaurants = self.parse_json_data(data)
                        if restaurants:
                            print(f"从JSON数据中提取到 {len(restaurants)} 个餐厅")
                            return restaurants
                    except:
                        continue
            
            return []
            
        except Exception as e:
            print(f"从JSON提取数据时出错: {e}")
            return []
    
    def parse_json_data(self, data):
        """解析JSON数据"""
        restaurants = []
        
        def find_restaurants(obj):
            if isinstance(obj, dict):
                # 查找可能包含餐厅信息的字段
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
                                        'category': item.get('category', item.get('categoryName', '')),
                                        'price': item.get('avgPrice', item.get('price', 0)),
                                        'review_count': item.get('reviewCount', 0)
                                    }
                                    restaurants.append(restaurant)
                    else:
                        find_restaurants(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_restaurants(item)
        
        find_restaurants(data)
        return restaurants
    
    def extract_restaurant_info(self, item):
        """提取单个餐厅信息"""
        try:
            restaurant = {}
            
            # 餐厅名称
            name_selectors = ['.shop-name', '.shopname', 'h3', '.title', 'a[title]', '.poi-name']
            for selector in name_selectors:
                elem = item.select_one(selector)
                if elem:
                    restaurant['name'] = elem.get_text(strip=True)
                    break
            
            # 评分
            rating_selectors = ['.shop-star', '.star', '.rating', '[class*="star"]', '.score']
            for selector in rating_selectors:
                elem = item.select_one(selector)
                if elem:
                    rating_text = elem.get_text(strip=True)
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        restaurant['rating'] = float(rating_match.group(1))
                    break
            
            # 地址
            address_selectors = ['.shop-addr', '.address', '.addr', '.location']
            for selector in address_selectors:
                elem = item.select_one(selector)
                if elem:
                    restaurant['address'] = elem.get_text(strip=True)
                    break
            
            # 价格
            price_selectors = ['.shop-price', '.price', '.avgprice', '.per-price']
            for selector in price_selectors:
                elem = item.select_one(selector)
                if elem:
                    price_text = elem.get_text(strip=True)
                    price_match = re.search(r'(\d+)', price_text)
                    if price_match:
                        restaurant['price_per_person'] = int(price_match.group(1))
                    break
            
            # 店铺ID
            shop_id = item.get('data-shopid') or item.get('data-id')
            if shop_id:
                restaurant['shop_id'] = shop_id
            
            return restaurant if restaurant.get('name') else None
            
        except Exception as e:
            print(f"提取餐厅信息时出错: {e}")
            return None
    
    def crawl_real_data(self):
        """爬取真实数据"""
        print("🚀 开始爬取真实的大众点评数据...")
        
        all_restaurants = []
        
        # 策略1: 尝试不同的搜索URL
        search_urls = [
            "http://www.dianping.com/dalian/ch10/g110",  # 大连自助餐
            "http://www.dianping.com/dalian/ch10",       # 大连美食
            "http://www.dianping.com/search/keyword/8/10_自助餐",
        ]
        
        for url in search_urls:
            print(f"\n🔄 尝试URL: {url}")
            response = self.smart_request(url)
            
            if response:
                # 保存页面用于调试
                with open('/Users/hal/Documents/GitHub/dianping_spider/real_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                restaurants = self.parse_restaurant_list(response.text)
                if restaurants:
                    all_restaurants.extend(restaurants)
                    print(f"✅ 从此URL获取到 {len(restaurants)} 个餐厅")
                    break
        
        # 策略2: 尝试移动端API
        if not all_restaurants:
            print("\n🔄 尝试移动端API...")
            mobile_response = self.try_mobile_api()
            if mobile_response:
                restaurants = self.parse_restaurant_list(mobile_response.text)
                if restaurants:
                    all_restaurants.extend(restaurants)
        
        # 保存数据
        if all_restaurants:
            self.save_real_data(all_restaurants)
            return all_restaurants
        else:
            print("❌ 未能获取到真实数据")
            return []
    
    def save_real_data(self, restaurants):
        """保存真实数据"""
        if not self.mongo_client or not restaurants:
            return
        
        try:
            # 清空之前的数据
            self.restaurants_collection.delete_many({})
            
            # 添加爬取时间
            for restaurant in restaurants:
                restaurant['crawl_time'] = time.time()
                restaurant['data_source'] = 'real_crawl'
            
            result = self.restaurants_collection.insert_many(restaurants)
            print(f"✅ 成功保存 {len(result.inserted_ids)} 条真实餐厅数据")
            
            # 展示数据
            self.display_real_data()
            
        except Exception as e:
            print(f"❌ 保存真实数据时出错: {e}")
    
    def display_real_data(self):
        """展示真实数据"""
        print("\n" + "="*60)
        print("🎉 真实大众点评数据")
        print("="*60)
        
        restaurants = list(self.restaurants_collection.find().limit(10))
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\n{i}. 餐厅: {restaurant.get('name', 'N/A')}")
            if restaurant.get('rating'):
                print(f"   评分: {restaurant['rating']} ⭐")
            if restaurant.get('address'):
                print(f"   地址: {restaurant['address']}")
            if restaurant.get('price_per_person'):
                print(f"   人均: ¥{restaurant['price_per_person']}")
            if restaurant.get('category'):
                print(f"   类型: {restaurant['category']}")

def main():
    print("=== 高级大众点评爬虫 ===")
    print("专注获取真实点评数据\n")
    
    crawler = AdvancedDianpingCrawler()
    restaurants = crawler.crawl_real_data()
    
    if restaurants:
        print(f"\n🎉 成功获取 {len(restaurants)} 条真实数据！")
    else:
        print("\n😞 暂时无法突破反爬限制，建议:")
        print("1. 更新Cookie配置")
        print("2. 使用代理服务")
        print("3. 降低请求频率")

if __name__ == "__main__":
    main()
