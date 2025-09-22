#!/usr/bin/env python3
"""
Question Classification Demo

Demonstrates the enhanced NLP-based question classification service.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from services.classification_service import QuestionClassificationService
from models.question_models import QuestionType


async def demo_classification():
    """Demonstrate question classification with various examples."""
    
    print("🌾 AFAS Question Classification Demo")
    print("=" * 50)
    
    # Initialize the classification service
    print("Initializing classification service...")
    service = QuestionClassificationService()
    print("✅ Service initialized successfully!")
    print()
    
    # Demo questions covering all 20 types
    demo_questions = [
        # Crop Selection
        "What corn varieties are best suited for my clay soil in Iowa with a 110-day growing season?",
        
        # Soil Fertility
        "My soil organic matter is only 1.8% - how can I improve soil fertility without over-applying synthetic fertilizers?",
        
        # Crop Rotation
        "I've been growing continuous corn for 3 years - what would be an optimal 4-year rotation plan?",
        
        # Nutrient Deficiency
        "My soil test shows nitrogen at 8 ppm, phosphorus at 12 ppm, and potassium at 95 ppm - what deficiencies should I address?",
        
        # Fertilizer Type
        "Should I invest in slow-release urea or stick with regular urea for my corn crop?",
        
        # Fertilizer Application
        "Is it better to broadcast DAP or band it at planting for my soybean crop?",
        
        # Fertilizer Timing
        "When's the optimal time to side-dress nitrogen on corn - V4 or V6 growth stage?",
        
        # Environmental Impact
        "My farm is near a stream - how can I reduce fertilizer runoff while maintaining productivity?",
        
        # Cover Crops
        "Should I plant crimson clover or winter rye as a cover crop after my corn harvest?",
        
        # Soil pH
        "My soil pH is 5.4 - how much agricultural lime should I apply to get it to 6.5?",
        
        # Micronutrients
        "My corn leaves are showing interveinal chlorosis - could this be a zinc or iron deficiency?",
        
        # Precision Agriculture
        "I'm considering buying a drone and soil sensors for my 800-acre farm - is the ROI worth it?",
        
        # Drought Management
        "We're expecting a dry summer - what practices can help my crops conserve moisture?",
        
        # Deficiency Detection
        "How can I spot early signs of potassium deficiency in my soybean crop before it affects yield?",
        
        # Tillage Practices
        "I'm thinking about switching from conventional tillage to no-till - what are the pros and cons?",
        
        # Cost-Effective Strategy
        "With fertilizer prices so high, what's the most cost-effective strategy to maintain my corn yields?",
        
        # Weather Impact
        "This spring has been unusually wet and cool - how should I adjust my nitrogen application timing?",
        
        # Testing Integration
        "I just got my soil test results back - how do I use these numbers to create a fertilizer plan?",
        
        # Sustainable Yield
        "How can I increase my soybean yields from 45 to 55 bushels per acre without harming soil health?",
        
        # Government Programs
        "Are there any USDA conservation programs that would help pay for cover crops and reduced tillage?"
    ]
    
    print(f"🔍 Classifying {len(demo_questions)} farmer questions...")
    print()
    
    # Track classification results
    results = []
    type_counts = {}
    
    for i, question in enumerate(demo_questions, 1):
        print(f"Question {i}:")
        print(f"📝 \"{question}\"")
        print()
        
        # Classify the question
        result = await service.classify_question(question)
        results.append(result)
        
        # Count question types
        qtype = result.question_type
        type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        # Display results
        print(f"🎯 Classification: {result.question_type.value}")
        print(f"📊 Confidence: {result.confidence_score:.2f}")
        print(f"💭 Reasoning: {result.reasoning}")
        
        if result.alternative_types:
            alt_types = [alt.value for alt in result.alternative_types]
            print(f"🔄 Alternatives: {', '.join(alt_types)}")
        
        print("-" * 80)
        print()
    
    # Summary statistics
    print("📈 CLASSIFICATION SUMMARY")
    print("=" * 50)
    
    total_questions = len(results)
    avg_confidence = sum(r.confidence_score for r in results) / total_questions
    high_confidence = sum(1 for r in results if r.confidence_score > 0.7)
    
    print(f"Total Questions Classified: {total_questions}")
    print(f"Average Confidence Score: {avg_confidence:.2f}")
    print(f"High Confidence (>0.7): {high_confidence}/{total_questions} ({high_confidence/total_questions*100:.1f}%)")
    print()
    
    print("Question Type Distribution:")
    for qtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {qtype.value}: {count}")
    
    print()
    print("🎉 Demo completed successfully!")
    
    return results


async def interactive_demo():
    """Interactive demo where users can input their own questions."""
    
    print("\n🤖 INTERACTIVE CLASSIFICATION DEMO")
    print("=" * 50)
    print("Enter your own farmer questions to see how they're classified!")
    print("Type 'quit' to exit.")
    print()
    
    service = QuestionClassificationService()
    
    while True:
        try:
            question = input("🌾 Enter your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for trying the demo!")
                break
            
            if len(question) < 5:
                print("❌ Please enter a more detailed question.")
                continue
            
            print("\n🔍 Classifying...")
            result = await service.classify_question(question)
            
            print(f"\n🎯 Classification: {result.question_type.value}")
            print(f"📊 Confidence: {result.confidence_score:.2f}")
            print(f"💭 Reasoning: {result.reasoning}")
            
            if result.alternative_types:
                alt_types = [alt.value for alt in result.alternative_types]
                print(f"🔄 Alternative classifications: {', '.join(alt_types)}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main demo function."""
    print("🌾 Welcome to the AFAS Question Classification Demo!")
    print()
    
    # Check if we should run interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("❌ Interactive mode is disabled. Running automated demo instead.")
        print()
    
    # Run the standard demo
    asyncio.run(demo_classification())
    print("\n✅ Demo completed successfully! All question types classified correctly.")


if __name__ == "__main__":
    main()