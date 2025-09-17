#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import random
import time
from datetime import datetime
from faker import Faker

class DianpingDataGenerator:
    def __init__(self):
        self.fake = Faker('zh_CN')
        
        # MongoDB连接
        try:
            self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
            self.db = self.mongo_client['dianping']
            self.restaurants_collection = self.db['restaurants']
            self.reviews_collection = self.db['reviews']
            print("✅ MongoDB连接成功")
        except Exception as e:
            print(f"❌ MongoDB连接失败: {e}")
            self.mongo_client = None
    
    def generate_restaurant_data(self, count=20):
        """生成餐厅数据"""
        restaurants = []
        
        # 大连地区的真实餐厅类型和区域
        restaurant_types = ['自助餐', '火锅', '烧烤', '海鲜', '东北菜', '川菜', '粤菜', '日料', '韩料', '西餐']
        districts = ['中山区', '西岗区', '沙河口区', '甘井子区', '旅顺口区', '金州区', '普兰店区']
        
        for i in range(count):
            restaurant = {
                'shop_id': f"shop_{random.randint(100000, 999999)}",
                'name': f"{self.fake.company()}{random.choice(['餐厅', '酒楼', '食府', '大酒店', '美食城'])}",
                'category': random.choice(restaurant_types),
                'rating': round(random.uniform(3.5, 4.8), 1),
                'price_per_person': random.randint(50, 300),
                'address': f"大连市{random.choice(districts)}{self.fake.street_address()}",
                'phone': self.fake.phone_number(),
                'business_hours': f"{random.randint(9, 11)}:00-{random.randint(20, 23)}:00",
                'taste_score': round(random.uniform(7.0, 9.0), 1),
                'environment_score': round(random.uniform(7.0, 9.0), 1),
                'service_score': round(random.uniform(7.0, 9.0), 1),
                'review_count': random.randint(50, 2000),
                'crawl_time': datetime.now(),
                'location': {
                    'latitude': round(random.uniform(38.8, 39.2), 6),
                    'longitude': round(random.uniform(121.4, 122.0), 6)
                }
            }
            restaurants.append(restaurant)
        
        return restaurants
    
    def generate_review_data(self, restaurant_id, count=10):
        """生成评论数据"""
        reviews = []
        
        review_templates = [
            "味道不错，环境很好，服务态度也很棒！",
            "性价比很高，菜品丰富，推荐！",
            "环境优雅，菜品精致，值得再来。",
            "服务很周到，菜品新鲜，口感很好。",
            "价格合理，分量足，味道正宗。",
            "装修很有特色，菜品创新，体验不错。",
            "老字号了，味道一如既往的好。",
            "朋友聚餐的好地方，氛围很棒。"
        ]
        
        for i in range(count):
            review = {
                'restaurant_id': restaurant_id,
                'user_name': self.fake.name(),
                'rating': random.randint(3, 5),
                'content': random.choice(review_templates) + f" {self.fake.sentence()}",
                'taste_score': random.randint(7, 10),
                'environment_score': random.randint(7, 10),
                'service_score': random.randint(7, 10),
                'review_date': self.fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d'),
                'useful_count': random.randint(0, 50),
                'crawl_time': datetime.now()
            }
            reviews.append(review)
        
        return reviews
    
    def save_to_mongodb(self):
        """保存数据到MongoDB"""
        if not self.mongo_client:
            print("❌ MongoDB未连接，无法保存数据")
            return
        
        print("🔄 正在生成餐厅数据...")
        restaurants = self.generate_restaurant_data(20)
        
        # 保存餐厅数据
        try:
            # 清空现有数据
            self.restaurants_collection.delete_many({})
            self.reviews_collection.delete_many({})
            
            result = self.restaurants_collection.insert_many(restaurants)
            print(f"✅ 成功保存 {len(result.inserted_ids)} 条餐厅数据")
            
            # 为每个餐厅生成评论数据
            print("🔄 正在生成评论数据...")
            all_reviews = []
            for restaurant in restaurants:
                reviews = self.generate_review_data(restaurant['shop_id'], random.randint(5, 15))
                all_reviews.extend(reviews)
            
            if all_reviews:
                result = self.reviews_collection.insert_many(all_reviews)
                print(f"✅ 成功保存 {len(result.inserted_ids)} 条评论数据")
            
            return True
            
        except Exception as e:
            print(f"❌ 保存数据时出错: {e}")
            return False
    
    def display_sample_data(self):
        """展示样本数据"""
        if not self.mongo_client:
            return
        
        print("\n" + "="*60)
        print("📊 餐厅数据样本")
        print("="*60)
        
        restaurants = list(self.restaurants_collection.find().limit(5))
        for i, restaurant in enumerate(restaurants, 1):
            print(f"\n{i}. 餐厅名称: {restaurant['name']}")
            print(f"   类型: {restaurant['category']}")
            print(f"   评分: {restaurant['rating']} ⭐")
            print(f"   人均: ¥{restaurant['price_per_person']}")
            print(f"   地址: {restaurant['address']}")
            print(f"   评论数: {restaurant['review_count']}")
        
        print("\n" + "="*60)
        print("💬 评论数据样本")
        print("="*60)
        
        reviews = list(self.reviews_collection.find().limit(5))
        for i, review in enumerate(reviews, 1):
            print(f"\n{i}. 用户: {review['user_name']}")
            print(f"   评分: {review['rating']} ⭐")
            print(f"   内容: {review['content']}")
            print(f"   日期: {review['review_date']}")
    
    def get_statistics(self):
        """获取数据统计"""
        if not self.mongo_client:
            return
        
        restaurant_count = self.restaurants_collection.count_documents({})
        review_count = self.reviews_collection.count_documents({})
        
        print("\n" + "="*60)
        print("📈 数据统计")
        print("="*60)
        print(f"餐厅总数: {restaurant_count}")
        print(f"评论总数: {review_count}")
        
        # 按类型统计
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_stats = list(self.restaurants_collection.aggregate(pipeline))
        
        print("\n餐厅类型分布:")
        for stat in category_stats:
            print(f"  {stat['_id']}: {stat['count']} 家")
        
        # 评分分布
        pipeline = [
            {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
            {"$sort": {"_id": -1}}
        ]
        rating_stats = list(self.restaurants_collection.aggregate(pipeline))
        
        print("\n评分分布:")
        for stat in rating_stats:
            print(f"  {stat['_id']} 分: {stat['count']} 家")

def main():
    print("=== 大众点评数据生成器 ===")
    print("由于反爬限制，使用模拟数据演示项目功能\n")
    
    generator = DianpingDataGenerator()
    
    # 生成并保存数据
    if generator.save_to_mongodb():
        print("\n🎉 数据生成完成！")
        
        # 展示样本数据
        generator.display_sample_data()
        
        # 展示统计信息
        generator.get_statistics()
        
        print("\n" + "="*60)
        print("🔍 数据查看方法:")
        print("="*60)
        print("1. 使用MongoDB客户端:")
        print("   mongosh")
        print("   use dianping")
        print("   db.restaurants.find().limit(5)")
        print("   db.reviews.find().limit(5)")
        print("\n2. 使用Python查询:")
        print("   from pymongo import MongoClient")
        print("   client = MongoClient('mongodb://localhost:27017/')")
        print("   db = client['dianping']")
        print("   restaurants = db.restaurants.find()")
    else:
        print("❌ 数据生成失败")

if __name__ == "__main__":
    main()
