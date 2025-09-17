#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import json
from bs4 import BeautifulSoup
import pymongo
from urllib.parse import urljoin

class SimpleDianpingCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://www.dianping.com"
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Cookie配置
        self.cookies = {
            '_hc.v': 'e8c70e5d-fb22-43af-2857-ffe83d9f7329.1758043300',
            '_lxsdk': '199538be002c8-0b02bd0c8c3bd3-16525636-708000-199538be002c8',
            '_lxsdk_cuid': '199538be002c8-0b02bd0c8c3bd3-16525636-708000-199538be002c8',
            '_lxsdk_s': '19955ae6eca-ef3-b42-2c7%7C%7C24',
            'fspop': 'test',
            'logan_session_token': 'm0iywvv5uwdsy0t9q92o'
        }
        
        # MongoDB连接
        try:
            self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
            self.db = self.mongo_client['dianping']
            self.collection = self.db['restaurants']
            print("✅ MongoDB连接成功")
        except Exception as e:
            print(f"❌ MongoDB连接失败: {e}")
            self.mongo_client = None
    
    def get_page(self, url, max_retries=3):
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                print(f"正在请求: {url} (尝试 {attempt + 1}/{max_retries})")
                
                # 随机延迟
                time.sleep(random.uniform(5, 10))
                
                response = self.session.get(
                    url, 
                    headers=self.headers, 
                    cookies=self.cookies,
                    timeout=15,
                    allow_redirects=True
                )
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应URL: {response.url}")
                
                if response.status_code == 200:
                    return response
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"请求异常: {e}")
                
            if attempt < max_retries - 1:
                wait_time = random.uniform(10, 20)
                print(f"等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)
        
        return None
    
    def parse_restaurant_info(self, html_content):
        """解析餐厅信息"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            restaurants = []
            
            # 尝试多种选择器来找到餐厅信息
            selectors = [
                '.shop-list .shop-item',
                '.shoplist .shopitem',
                '.shop-wrap',
                '.list-item',
                '[data-shopid]'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    print(f"找到 {len(items)} 个餐厅项目 (使用选择器: {selector})")
                    
                    for item in items:
                        restaurant = self.extract_restaurant_data(item)
                        if restaurant:
                            restaurants.append(restaurant)
                    break
            
            return restaurants
            
        except Exception as e:
            print(f"解析HTML时出错: {e}")
            return []
    
    def extract_restaurant_data(self, item):
        """提取单个餐厅数据"""
        try:
            restaurant = {}
            
            # 提取餐厅名称
            name_selectors = ['.shop-name', '.shopname', 'h3', '.title', 'a[title]']
            for selector in name_selectors:
                name_elem = item.select_one(selector)
                if name_elem:
                    restaurant['name'] = name_elem.get_text(strip=True)
                    break
            
            # 提取评分
            rating_selectors = ['.shop-star', '.star', '.rating', '[class*="star"]']
            for selector in rating_selectors:
                rating_elem = item.select_one(selector)
                if rating_elem:
                    restaurant['rating'] = rating_elem.get_text(strip=True)
                    break
            
            # 提取地址
            address_selectors = ['.shop-addr', '.address', '.addr']
            for selector in address_selectors:
                addr_elem = item.select_one(selector)
                if addr_elem:
                    restaurant['address'] = addr_elem.get_text(strip=True)
                    break
            
            # 提取价格
            price_selectors = ['.shop-price', '.price', '.avgprice']
            for selector in price_selectors:
                price_elem = item.select_one(selector)
                if price_elem:
                    restaurant['price'] = price_elem.get_text(strip=True)
                    break
            
            # 提取店铺ID
            shop_id = item.get('data-shopid') or item.get('data-id')
            if shop_id:
                restaurant['shop_id'] = shop_id
            
            return restaurant if restaurant.get('name') else None
            
        except Exception as e:
            print(f"提取餐厅数据时出错: {e}")
            return None
    
    def save_to_mongodb(self, restaurants):
        """保存到MongoDB"""
        if not self.mongo_client or not restaurants:
            return
        
        try:
            result = self.collection.insert_many(restaurants)
            print(f"✅ 成功保存 {len(result.inserted_ids)} 条餐厅数据到MongoDB")
        except Exception as e:
            print(f"❌ 保存到MongoDB时出错: {e}")
    
    def crawl_search_page(self, keyword="自助餐", location="大连"):
        """爬取搜索页面"""
        print(f"开始爬取: {keyword} - {location}")
        
        # 构建搜索URL
        search_urls = [
            f"http://www.dianping.com/dalian/ch10/g110",  # 大连自助餐
            f"http://www.dianping.com/search/keyword/8/10_{keyword}",  # 通用搜索
            f"http://www.dianping.com/dalian/food",  # 大连美食
        ]
        
        all_restaurants = []
        
        for url in search_urls:
            print(f"\n尝试URL: {url}")
            response = self.get_page(url)
            
            if response:
                print(f"页面内容长度: {len(response.text)}")
                
                # 保存HTML用于调试
                with open('/Users/hal/Documents/GitHub/dianping_spider/debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("页面内容已保存到 debug_page.html")
                
                restaurants = self.parse_restaurant_info(response.text)
                if restaurants:
                    all_restaurants.extend(restaurants)
                    print(f"从此页面提取到 {len(restaurants)} 个餐厅")
                    break
                else:
                    print("未能从此页面提取到餐厅信息")
            else:
                print("无法获取页面内容")
        
        if all_restaurants:
            print(f"\n总共获取到 {len(all_restaurants)} 个餐厅信息:")
            for i, restaurant in enumerate(all_restaurants[:5], 1):  # 显示前5个
                print(f"{i}. {restaurant}")
            
            self.save_to_mongodb(all_restaurants)
            return all_restaurants
        else:
            print("❌ 未能获取到任何餐厅数据")
            return []

def main():
    print("=== 简化版大众点评爬虫 ===\n")
    
    crawler = SimpleDianpingCrawler()
    restaurants = crawler.crawl_search_page()
    
    if restaurants:
        print(f"\n🎉 爬取成功！获取到 {len(restaurants)} 条餐厅数据")
    else:
        print("\n😞 爬取失败，请检查网络连接和Cookie配置")

if __name__ == "__main__":
    main()
