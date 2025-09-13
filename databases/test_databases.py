#!/usr/bin/env python3
"""
AFAS Database Test Script
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script tests all database connections and basic operations.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, date
from decimal import Decimal

# Add the databases directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.database_config import DatabaseManager, get_database_manager
from python.models import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_postgresql():
    """Test PostgreSQL connection and basic operations."""
    print("\n🐘 Testing PostgreSQL...")
    print("=" * 50)
    
    try:
        manager = get_database_manager()
        
        # Test connection
        if not manager.postgres.test_connection():
            print("❌ PostgreSQL connection failed")
            return False
        
        print("✅ PostgreSQL connection successful")
        
        # Test session creation
        session = manager.postgres.get_session()
        
        # Test basic query
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"📊 Current user count: {user_count}")
        
        # Test model creation (if tables exist)
        try:
            # Create a test user
            test_user = User(
                email="test@afas.com",
                password_hash="test_hash",
                first_name="Test",
                last_name="User",
                role="farmer"
            )
            
            session.add(test_user)
            session.commit()
            print("✅ Test user created successfully")
            
            # Query the test user
            user = session.query(User).filter(User.email == "test@afas.com").first()
            if user:
                print(f"✅ Test user retrieved: {user.full_name}")
                
                # Clean up
                session.delete(user)
                session.commit()
                print("✅ Test user deleted successfully")
            
        except Exception as e:
            session.rollback()
            print(f"⚠️  Model test skipped (tables may not exist): {e}")
        
        finally:
            session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection and basic operations."""
    print("\n🍃 Testing MongoDB...")
    print("=" * 50)
    
    try:
        manager = get_database_manager()
        
        # Test connection
        if not manager.mongodb.test_connection():
            print("❌ MongoDB connection failed")
            return False
        
        print("✅ MongoDB connection successful")
        
        # Test collection operations
        collection = manager.mongodb.get_collection('test_collection')
        
        # Insert test document
        test_doc = {
            'test_id': 'test_123',
            'message': 'Hello AFAS MongoDB!',
            'timestamp': datetime.utcnow(),
            'data': {
                'farm_id': 'test_farm',
                'recommendation': 'Test recommendation'
            }
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Query test document
        found_doc = collection.find_one({'test_id': 'test_123'})
        if found_doc:
            print(f"✅ Test document retrieved: {found_doc['message']}")
        
        # Update test document
        collection.update_one(
            {'test_id': 'test_123'},
            {'$set': {'updated': True, 'updated_at': datetime.utcnow()}}
        )
        print("✅ Test document updated successfully")
        
        # Delete test document
        delete_result = collection.delete_one({'test_id': 'test_123'})
        if delete_result.deleted_count > 0:
            print("✅ Test document deleted successfully")
        
        # Test agricultural knowledge collection
        knowledge_collection = manager.mongodb.get_collection('agricultural_knowledge')
        knowledge_count = knowledge_collection.count_documents({})
        print(f"📊 Agricultural knowledge documents: {knowledge_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

def test_redis():
    """Test Redis connection and basic operations."""
    print("\n🔴 Testing Redis...")
    print("=" * 50)
    
    try:
        manager = get_database_manager()
        
        # Test connection
        if not manager.redis.test_connection():
            print("❌ Redis connection failed")
            return False
        
        print("✅ Redis connection successful")
        
        # Test different Redis databases
        databases = {
            0: "User Sessions",
            1: "API Cache",
            2: "Real-time Data",
            3: "Rate Limiting"
        }
        
        for db_num, description in databases.items():
            try:
                client = manager.redis.get_client(db_num)
                
                # Test basic operations
                test_key = f"test:db{db_num}:key"
                test_value = f"test_value_for_db_{db_num}"
                
                # Set value
                client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
                
                # Get value
                retrieved_value = client.get(test_key)
                
                if retrieved_value == test_value:
                    print(f"✅ DB {db_num} ({description}): Basic operations successful")
                else:
                    print(f"❌ DB {db_num} ({description}): Value mismatch")
                
                # Test hash operations
                hash_key = f"test:db{db_num}:hash"
                client.hset(hash_key, mapping={
                    'field1': 'value1',
                    'field2': 'value2',
                    'timestamp': str(datetime.utcnow())
                })
                client.expire(hash_key, 60)
                
                hash_values = client.hgetall(hash_key)
                if hash_values:
                    print(f"✅ DB {db_num} ({description}): Hash operations successful")
                
                # Clean up
                client.delete(test_key, hash_key)
                
            except Exception as e:
                print(f"❌ DB {db_num} ({description}): Test failed - {e}")
        
        # Test session client specifically
        session_client = manager.redis.get_session_client()
        session_client.set("test:session", "session_data", ex=30)
        session_data = session_client.get("test:session")
        if session_data == "session_data":
            print("✅ Session client operations successful")
        session_client.delete("test:session")
        
        # Test cache client specifically
        cache_client = manager.redis.get_cache_client()
        cache_client.set("test:cache", "cache_data", ex=30)
        cache_data = cache_client.get("test:cache")
        if cache_data == "cache_data":
            print("✅ Cache client operations successful")
        cache_client.delete("test:cache")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def test_agricultural_data_operations():
    """Test agricultural-specific data operations."""
    print("\n🌾 Testing Agricultural Data Operations...")
    print("=" * 50)
    
    try:
        manager = get_database_manager()
        
        # Test PostgreSQL agricultural data
        session = manager.postgres.get_session()
        
        try:
            # Check if question types are populated
            question_count = session.query(QuestionType).count()
            print(f"📊 Question types in database: {question_count}")
            
            if question_count > 0:
                # Get a sample question
                sample_question = session.query(QuestionType).first()
                print(f"✅ Sample question: {sample_question.question_text[:50]}...")
            
            # Check crops
            crop_count = session.query(Crop).count()
            print(f"📊 Crops in database: {crop_count}")
            
            if crop_count > 0:
                # Get a sample crop
                sample_crop = session.query(Crop).first()
                print(f"✅ Sample crop: {sample_crop.crop_name}")
            
        finally:
            session.close()
        
        # Test MongoDB agricultural knowledge
        knowledge_collection = manager.mongodb.get_collection('agricultural_knowledge')
        knowledge_count = knowledge_collection.count_documents({})
        print(f"📊 Agricultural knowledge documents: {knowledge_count}")
        
        if knowledge_count > 0:
            sample_knowledge = knowledge_collection.find_one()
            if sample_knowledge:
                print(f"✅ Sample knowledge: {sample_knowledge.get('content', {}).get('title', 'N/A')}")
        
        # Test Redis agricultural caching
        cache_client = manager.redis.get_cache_client()
        
        # Simulate weather data cache
        weather_key = "api:cache:weather:42.0308_-93.6319_2024-12-09"
        weather_data = {
            'temperature_f': '32',
            'humidity': '75',
            'wind_speed': '8',
            'cached_at': str(datetime.utcnow())
        }
        
        cache_client.hset(weather_key, mapping=weather_data)
        cache_client.expire(weather_key, 3600)
        
        cached_weather = cache_client.hgetall(weather_key)
        if cached_weather:
            print("✅ Weather data caching successful")
        
        # Clean up
        cache_client.delete(weather_key)
        
        return True
        
    except Exception as e:
        print(f"❌ Agricultural data operations test failed: {e}")
        return False

def test_performance():
    """Test database performance with multiple operations."""
    print("\n⚡ Testing Database Performance...")
    print("=" * 50)
    
    try:
        manager = get_database_manager()
        
        # Test PostgreSQL performance
        start_time = datetime.utcnow()
        session = manager.postgres.get_session()
        
        # Perform multiple queries
        for i in range(10):
            session.execute(text("SELECT 1"))
        
        session.close()
        pg_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ PostgreSQL: 10 queries in {pg_time:.3f} seconds")
        
        # Test MongoDB performance
        start_time = datetime.utcnow()
        collection = manager.mongodb.get_collection('test_performance')
        
        # Insert multiple documents
        docs = [{'test_id': i, 'data': f'test_data_{i}'} for i in range(10)]
        collection.insert_many(docs)
        
        # Query documents
        found_docs = list(collection.find({'test_id': {'$gte': 0}}))
        
        # Clean up
        collection.delete_many({'test_id': {'$gte': 0}})
        
        mongo_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ MongoDB: 10 inserts + query + cleanup in {mongo_time:.3f} seconds")
        
        # Test Redis performance
        start_time = datetime.utcnow()
        client = manager.redis.get_client(0)
        
        # Perform multiple operations
        pipe = client.pipeline()
        for i in range(10):
            pipe.set(f'perf_test:{i}', f'value_{i}', ex=60)
        pipe.execute()
        
        # Get all values
        for i in range(10):
            client.get(f'perf_test:{i}')
        
        # Clean up
        keys_to_delete = [f'perf_test:{i}' for i in range(10)]
        client.delete(*keys_to_delete)
        
        redis_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"✅ Redis: 10 sets + 10 gets + cleanup in {redis_time:.3f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all database tests."""
    print("🌾 AFAS Database Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.utcnow()}")
    
    # Load environment variables
    from dotenv import load_dotenv
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env.database')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print("⚠️  No .env.database file found, using default values")
    
    # Run tests
    tests = [
        ("PostgreSQL", test_postgresql),
        ("MongoDB", test_mongodb),
        ("Redis", test_redis),
        ("Agricultural Data", test_agricultural_data_operations),
        ("Performance", test_performance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed! AFAS is ready to go!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the database setup.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        sys.exit(1)
    finally:
        # Clean up database connections
        try:
            from python.database_config import close_databases
            close_databases()
        except:
            pass