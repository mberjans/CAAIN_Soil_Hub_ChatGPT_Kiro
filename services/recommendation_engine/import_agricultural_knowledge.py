#!/usr/bin/env python3
"""
AFAS Agricultural Knowledge Base Import Script
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This script imports the comprehensive agricultural knowledge for Questions 1-5
into the MongoDB knowledge base for use by the recommendation engine.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../databases/python'))

try:
    from database_config import get_mongodb_collection
    MONGODB_AVAILABLE = True
except ImportError:
    print("⚠️  MongoDB connection not available - running in simulation mode")
    MONGODB_AVAILABLE = False

print("🌾 AFAS Agricultural Knowledge Base Import")
print("=" * 60)

def load_knowledge_from_json(filename: str) -> List[Dict[str, Any]]:
    """Load knowledge items from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            knowledge_data = json.load(f)
        print(f"✅ Loaded {len(knowledge_data)} knowledge items from {filename}")
        return knowledge_data
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {filename}: {e}")
        return []

def validate_knowledge_item(item: Dict[str, Any]) -> bool:
    """Validate a knowledge item has required fields."""
    required_fields = [
        'knowledge_id', 'category', 'subcategory', 'title', 
        'description', 'guidelines', 'tags'
    ]
    
    for field in required_fields:
        if field not in item or not item[field]:
            print(f"❌ Missing required field '{field}' in knowledge item")
            return False
    
    # Validate guidelines is a list
    if not isinstance(item['guidelines'], list) or len(item['guidelines']) == 0:
        print(f"❌ Guidelines must be a non-empty list")
        return False
    
    # Validate tags is a list
    if not isinstance(item['tags'], list) or len(item['tags']) == 0:
        print(f"❌ Tags must be a non-empty list")
        return False
    
    return True

def import_to_mongodb(knowledge_items: List[Dict[str, Any]]) -> bool:
    """Import knowledge items to MongoDB."""
    if not MONGODB_AVAILABLE:
        print("📝 Simulating MongoDB import...")
        for item in knowledge_items:
            print(f"   Would import: {item['knowledge_id']} - {item['title']}")
        return True
    
    try:
        # Get MongoDB collection
        collection = get_mongodb_collection('agricultural_knowledge')
        
        # Clear existing knowledge (for clean import)
        print("🗑️  Clearing existing agricultural knowledge...")
        result = collection.delete_many({})
        print(f"   Deleted {result.deleted_count} existing items")
        
        # Import new knowledge items
        print("📥 Importing new agricultural knowledge...")
        
        imported_count = 0
        for item in knowledge_items:
            try:
                # Check if item already exists
                existing = collection.find_one({"knowledge_id": item["knowledge_id"]})
                
                if existing:
                    # Update existing item
                    item["updated_at"] = datetime.utcnow().isoformat()
                    result = collection.replace_one(
                        {"knowledge_id": item["knowledge_id"]}, 
                        item
                    )
                    if result.modified_count > 0:
                        print(f"   ✅ Updated: {item['knowledge_id']}")
                        imported_count += 1
                else:
                    # Insert new item
                    item["created_at"] = datetime.utcnow().isoformat()
                    item["updated_at"] = datetime.utcnow().isoformat()
                    result = collection.insert_one(item)
                    if result.inserted_id:
                        print(f"   ✅ Imported: {item['knowledge_id']}")
                        imported_count += 1
                        
            except Exception as e:
                print(f"   ❌ Failed to import {item.get('knowledge_id', 'unknown')}: {e}")
        
        print(f"\n📊 Import Summary:")
        print(f"   Successfully imported: {imported_count}/{len(knowledge_items)} items")
        
        # Create indexes for efficient querying
        print("\n🔍 Creating database indexes...")
        try:
            collection.create_index([("knowledge_id", 1)], unique=True)
            collection.create_index([("category", 1), ("subcategory", 1)])
            collection.create_index([("tags", 1)])
            collection.create_index([
                ("title", "text"),
                ("description", "text"),
                ("tags", "text")
            ], name="text_search")
            print("   ✅ Database indexes created successfully")
        except Exception as e:
            print(f"   ⚠️  Index creation warning: {e}")
        
        return imported_count == len(knowledge_items)
        
    except Exception as e:
        print(f"❌ MongoDB import failed: {e}")
        return False

def verify_import(knowledge_items: List[Dict[str, Any]]) -> bool:
    """Verify the import was successful."""
    if not MONGODB_AVAILABLE:
        print("✅ Simulation mode - skipping verification")
        return True
    
    try:
        collection = get_mongodb_collection('agricultural_knowledge')
        
        print("\n🔍 Verifying import...")
        
        # Check total count
        total_count = collection.count_documents({})
        expected_count = len(knowledge_items)
        
        print(f"   Total items in database: {total_count}")
        print(f"   Expected items: {expected_count}")
        
        if total_count != expected_count:
            print(f"   ❌ Count mismatch!")
            return False
        
        # Check each knowledge item exists
        missing_items = []
        for item in knowledge_items:
            existing = collection.find_one({"knowledge_id": item["knowledge_id"]})
            if not existing:
                missing_items.append(item["knowledge_id"])
        
        if missing_items:
            print(f"   ❌ Missing items: {missing_items}")
            return False
        
        # Check categories
        categories = collection.distinct("category")
        print(f"   Categories in database: {sorted(categories)}")
        
        # Check expert validation
        expert_validated = collection.count_documents({"expert_validated": True})
        print(f"   Expert validated items: {expert_validated}/{total_count}")
        
        print("   ✅ Import verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def generate_knowledge_summary(knowledge_items: List[Dict[str, Any]]):
    """Generate a summary of the imported knowledge."""
    
    print(f"\n📋 Agricultural Knowledge Base Summary")
    print("-" * 50)
    
    # Count by category
    category_counts = {}
    subcategory_counts = {}
    tag_counts = {}
    
    for item in knowledge_items:
        # Categories
        category = item['category']
        category_counts[category] = category_counts.get(category, 0) + 1
        
        # Subcategories
        subcategory = f"{category}.{item['subcategory']}"
        subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1
        
        # Tags
        for tag in item.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print(f"📊 Knowledge Distribution:")
    print(f"   Total Items: {len(knowledge_items)}")
    
    print(f"\n   By Category:")
    for category, count in sorted(category_counts.items()):
        print(f"     • {category.replace('_', ' ').title()}: {count} items")
    
    print(f"\n   By Subcategory:")
    for subcategory, count in sorted(subcategory_counts.items()):
        category, sub = subcategory.split('.', 1)
        print(f"     • {category.replace('_', ' ').title()} > {sub.replace('_', ' ').title()}: {count} items")
    
    print(f"\n   Top Tags:")
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    for tag, count in sorted_tags[:10]:
        print(f"     • {tag}: {count} items")
    
    # Quality metrics
    expert_validated = sum(1 for item in knowledge_items if item.get('expert_validated', False))
    with_calculations = sum(1 for item in knowledge_items if item.get('calculations'))
    with_regional = sum(1 for item in knowledge_items if item.get('regional_variations'))
    
    print(f"\n📈 Quality Metrics:")
    print(f"   Expert Validated: {expert_validated}/{len(knowledge_items)} ({expert_validated/len(knowledge_items)*100:.1f}%)")
    print(f"   With Calculations: {with_calculations}/{len(knowledge_items)} ({with_calculations/len(knowledge_items)*100:.1f}%)")
    print(f"   With Regional Variations: {with_regional}/{len(knowledge_items)} ({with_regional/len(knowledge_items)*100:.1f}%)")
    
    # Coverage by question
    print(f"\n🎯 Question Coverage:")
    question_mapping = {
        "crop_selection": "Question 1: Crop Selection",
        "soil_fertility": "Question 2: Soil Fertility", 
        "crop_rotation": "Question 3: Crop Rotation",
        "nutrient_deficiency": "Question 4: Nutrient Deficiency",
        "fertilizer_selection": "Question 5: Fertilizer Selection"
    }
    
    for key, question in question_mapping.items():
        count = sum(1 for item in knowledge_items 
                   if key in item.get('tags', []) or 
                      key in item.get('subcategory', ''))
        print(f"   • {question}: {count} knowledge items")

def main():
    """Main function to import agricultural knowledge."""
    
    print("🚀 Starting Agricultural Knowledge Import")
    print("-" * 60)
    
    # Load knowledge from JSON file
    knowledge_file = "agricultural_knowledge_questions_1_5.json"
    
    if not os.path.exists(knowledge_file):
        print(f"❌ Knowledge file not found: {knowledge_file}")
        print("   Please run populate_agricultural_knowledge.py first")
        return 1
    
    knowledge_items = load_knowledge_from_json(knowledge_file)
    
    if not knowledge_items:
        print("❌ No knowledge items loaded")
        return 1
    
    # Validate knowledge items
    print(f"\n🔍 Validating {len(knowledge_items)} knowledge items...")
    valid_items = []
    
    for i, item in enumerate(knowledge_items):
        if validate_knowledge_item(item):
            valid_items.append(item)
        else:
            print(f"❌ Invalid knowledge item at index {i}")
    
    print(f"   ✅ {len(valid_items)}/{len(knowledge_items)} items are valid")
    
    if len(valid_items) != len(knowledge_items):
        print("❌ Some knowledge items failed validation")
        return 1
    
    # Import to MongoDB
    print(f"\n📥 Importing to MongoDB...")
    import_success = import_to_mongodb(valid_items)
    
    if not import_success:
        print("❌ Import failed")
        return 1
    
    # Verify import
    verification_success = verify_import(valid_items)
    
    if not verification_success:
        print("❌ Import verification failed")
        return 1
    
    # Generate summary
    generate_knowledge_summary(valid_items)
    
    print(f"\n🎉 Agricultural Knowledge Base Import Completed Successfully!")
    
    if MONGODB_AVAILABLE:
        print(f"\n📝 Next Steps:")
        print(f"   1. Test knowledge retrieval with recommendation engine")
        print(f"   2. Verify API endpoints can access agricultural knowledge")
        print(f"   3. Run integration tests for Questions 1-5")
        print(f"   4. Validate recommendations with agricultural experts")
    else:
        print(f"\n📝 To complete the import:")
        print(f"   1. Set up MongoDB connection in database_config.py")
        print(f"   2. Re-run this script to import to actual database")
        print(f"   3. Test knowledge base integration")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)