#!/usr/bin/env python3
"""
Script to uncheck the 156 wrongly marked tasks in docs/checklist.md
"""

import re

# List of all 156 incorrectly marked tasks that need to be unchecked
TASKS_TO_UNCHECK = [
    # TICKET-023: Fertilizer Application Method (15 tasks)
    "TICKET-023_fertilizer-application-method-1.1",
    "TICKET-023_fertilizer-application-method-1.2", 
    "TICKET-023_fertilizer-application-method-1.3",
    "TICKET-023_fertilizer-application-method-2.1",
    "TICKET-023_fertilizer-application-method-2.2",
    "TICKET-023_fertilizer-application-method-2.3",
    "TICKET-023_fertilizer-application-method-3.1",
    "TICKET-023_fertilizer-application-method-3.2",
    "TICKET-023_fertilizer-application-method-3.3",
    "TICKET-023_fertilizer-application-method-10.1",
    "TICKET-023_fertilizer-application-method-10.2",
    "TICKET-023_fertilizer-application-method-11.1",
    "TICKET-023_fertilizer-application-method-11.2",
    "TICKET-023_fertilizer-application-method-12.1",
    "TICKET-023_fertilizer-application-method-12.2",
    
    # TICKET-006: Fertilizer Strategy Optimization (12 tasks)
    "TICKET-006_fertilizer-strategy-optimization-1.1",
    "TICKET-006_fertilizer-strategy-optimization-1.2",
    "TICKET-006_fertilizer-strategy-optimization-1.3",
    "TICKET-006_fertilizer-strategy-optimization-2.1",
    "TICKET-006_fertilizer-strategy-optimization-2.2",
    "TICKET-006_fertilizer-strategy-optimization-2.3",
    "TICKET-006_fertilizer-strategy-optimization-3.1",
    "TICKET-006_fertilizer-strategy-optimization-3.2",
    "TICKET-006_fertilizer-strategy-optimization-3.3",
    "TICKET-006_fertilizer-strategy-optimization-10.1",
    "TICKET-006_fertilizer-strategy-optimization-10.2",
    "TICKET-006_fertilizer-strategy-optimization-11.1",
    
    # TICKET-010: Fertilizer Timing Optimization (12 tasks)
    "TICKET-010_fertilizer-timing-optimization-1.1",
    "TICKET-010_fertilizer-timing-optimization-1.2",
    "TICKET-010_fertilizer-timing-optimization-1.3",
    "TICKET-010_fertilizer-timing-optimization-2.1",
    "TICKET-010_fertilizer-timing-optimization-2.2",
    "TICKET-010_fertilizer-timing-optimization-2.3",
    "TICKET-010_fertilizer-timing-optimization-3.1",
    "TICKET-010_fertilizer-timing-optimization-3.2",
    "TICKET-010_fertilizer-timing-optimization-3.3",
    "TICKET-010_fertilizer-timing-optimization-10.1",
    "TICKET-010_fertilizer-timing-optimization-10.2",
    "TICKET-010_fertilizer-timing-optimization-11.1",
    
    # TICKET-011: Fertilizer Type Selection (18 tasks)
    "TICKET-011_fertilizer-type-selection-1.1",
    "TICKET-011_fertilizer-type-selection-1.2",
    "TICKET-011_fertilizer-type-selection-1.3",
    "TICKET-011_fertilizer-type-selection-2.1",
    "TICKET-011_fertilizer-type-selection-2.2",
    "TICKET-011_fertilizer-type-selection-2.3",
    "TICKET-011_fertilizer-type-selection-3.1",
    "TICKET-011_fertilizer-type-selection-3.2",
    "TICKET-011_fertilizer-type-selection-3.3",
    "TICKET-011_fertilizer-type-selection-4.1",
    "TICKET-011_fertilizer-type-selection-4.2",
    "TICKET-011_fertilizer-type-selection-4.3",
    "TICKET-011_fertilizer-type-selection-10.1",
    "TICKET-011_fertilizer-type-selection-10.2",
    "TICKET-011_fertilizer-type-selection-11.1",
    "TICKET-011_fertilizer-type-selection-11.2",
    "TICKET-011_fertilizer-type-selection-12.1",
    "TICKET-011_fertilizer-type-selection-12.2",
    
    # TICKET-016: Micronutrient Management (18 tasks)
    "TICKET-016_micronutrient-management-1.1",
    "TICKET-016_micronutrient-management-1.2",
    "TICKET-016_micronutrient-management-1.3",
    "TICKET-016_micronutrient-management-2.1",
    "TICKET-016_micronutrient-management-2.2",
    "TICKET-016_micronutrient-management-2.3",
    "TICKET-016_micronutrient-management-3.1",
    "TICKET-016_micronutrient-management-3.2",
    "TICKET-016_micronutrient-management-3.3",
    "TICKET-016_micronutrient-management-4.1",
    "TICKET-016_micronutrient-management-4.2",
    "TICKET-016_micronutrient-management-4.3",
    "TICKET-016_micronutrient-management-10.1",
    "TICKET-016_micronutrient-management-10.2",
    "TICKET-016_micronutrient-management-11.1",
    "TICKET-016_micronutrient-management-11.2",
    "TICKET-016_micronutrient-management-12.1",
    "TICKET-016_micronutrient-management-12.2",
    
    # TICKET-024: Runoff Prevention (15 tasks)
    "TICKET-024_runoff-prevention-1.1",
    "TICKET-024_runoff-prevention-1.2",
    "TICKET-024_runoff-prevention-1.3",
    "TICKET-024_runoff-prevention-2.1",
    "TICKET-024_runoff-prevention-2.2",
    "TICKET-024_runoff-prevention-2.3",
    "TICKET-024_runoff-prevention-3.1",
    "TICKET-024_runoff-prevention-3.2",
    "TICKET-024_runoff-prevention-3.3",
    "TICKET-024_runoff-prevention-10.1",
    "TICKET-024_runoff-prevention-10.2",
    "TICKET-024_runoff-prevention-11.1",
    "TICKET-024_runoff-prevention-11.2",
    "TICKET-024_runoff-prevention-12.1",
    "TICKET-024_runoff-prevention-12.2",
    
    # TICKET-017: Soil Tissue Test Integration (15 tasks)
    "TICKET-017_soil-tissue-test-integration-1.1",
    "TICKET-017_soil-tissue-test-integration-1.2",
    "TICKET-017_soil-tissue-test-integration-1.3",
    "TICKET-017_soil-tissue-test-integration-2.1",
    "TICKET-017_soil-tissue-test-integration-2.2",
    "TICKET-017_soil-tissue-test-integration-2.3",
    "TICKET-017_soil-tissue-test-integration-3.1",
    "TICKET-017_soil-tissue-test-integration-3.2",
    "TICKET-017_soil-tissue-test-integration-3.3",
    "TICKET-017_soil-tissue-test-integration-10.1",
    "TICKET-017_soil-tissue-test-integration-10.2",
    "TICKET-017_soil-tissue-test-integration-11.1",
    "TICKET-017_soil-tissue-test-integration-11.2",
    "TICKET-017_soil-tissue-test-integration-12.1",
    "TICKET-017_soil-tissue-test-integration-12.2",
    
    # TICKET-018: Tillage Practice Recommendations (15 tasks)
    "TICKET-018_tillage-practice-recommendations-1.1",
    "TICKET-018_tillage-practice-recommendations-1.2",
    "TICKET-018_tillage-practice-recommendations-1.3",
    "TICKET-018_tillage-practice-recommendations-2.1",
    "TICKET-018_tillage-practice-recommendations-2.2",
    "TICKET-018_tillage-practice-recommendations-2.3",
    "TICKET-018_tillage-practice-recommendations-3.1",
    "TICKET-018_tillage-practice-recommendations-3.2",
    "TICKET-018_tillage-practice-recommendations-3.3",
    "TICKET-018_tillage-practice-recommendations-10.1",
    "TICKET-018_tillage-practice-recommendations-10.2",
    "TICKET-018_tillage-practice-recommendations-11.1",
    "TICKET-018_tillage-practice-recommendations-11.2",
    "TICKET-018_tillage-practice-recommendations-12.1",
    "TICKET-018_tillage-practice-recommendations-12.2",
    
    # TICKET-009: Weather Impact Analysis (15 tasks)
    "TICKET-009_weather-impact-analysis-1.1",
    "TICKET-009_weather-impact-analysis-1.2",
    "TICKET-009_weather-impact-analysis-1.3",
    "TICKET-009_weather-impact-analysis-2.1",
    "TICKET-009_weather-impact-analysis-2.2",
    "TICKET-009_weather-impact-analysis-2.3",
    "TICKET-009_weather-impact-analysis-3.1",
    "TICKET-009_weather-impact-analysis-3.2",
    "TICKET-009_weather-impact-analysis-3.3",
    "TICKET-009_weather-impact-analysis-10.1",
    "TICKET-009_weather-impact-analysis-10.2",
    "TICKET-009_weather-impact-analysis-11.1",
    "TICKET-009_weather-impact-analysis-11.2",
    "TICKET-009_weather-impact-analysis-12.1",
    "TICKET-009_weather-impact-analysis-12.2",
    
    # TICKET-007: Nutrient Deficiency Detection (21 tasks)
    "TICKET-007_nutrient-deficiency-detection-1.1",
    "TICKET-007_nutrient-deficiency-detection-1.2",
    "TICKET-007_nutrient-deficiency-detection-1.3",
    "TICKET-007_nutrient-deficiency-detection-2.1",
    "TICKET-007_nutrient-deficiency-detection-2.2",
    "TICKET-007_nutrient-deficiency-detection-2.3",
    "TICKET-007_nutrient-deficiency-detection-3.1",
    "TICKET-007_nutrient-deficiency-detection-3.2",
    "TICKET-007_nutrient-deficiency-detection-3.3",
    "TICKET-007_nutrient-deficiency-detection-4.1",
    "TICKET-007_nutrient-deficiency-detection-4.2",
    "TICKET-007_nutrient-deficiency-detection-4.3",
    "TICKET-007_nutrient-deficiency-detection-5.1",
    "TICKET-007_nutrient-deficiency-detection-5.2",
    "TICKET-007_nutrient-deficiency-detection-5.3",
    "TICKET-007_nutrient-deficiency-detection-6.1",
    "TICKET-007_nutrient-deficiency-detection-6.2",
    "TICKET-007_nutrient-deficiency-detection-6.3",
    "TICKET-007_nutrient-deficiency-detection-7.1",
    "TICKET-007_nutrient-deficiency-detection-7.2",
    "TICKET-007_nutrient-deficiency-detection-7.3",
]

def uncheck_tasks():
    """Uncheck all 156 wrongly marked tasks in docs/checklist.md"""
    
    # Read the current checklist
    with open('docs/checklist.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = 0
    tasks_not_found = []
    
    # Process each task
    for task in TASKS_TO_UNCHECK:
        # Pattern to match: - [x] TASK_ID (any description)
        pattern = rf'^- \[x\] {re.escape(task)} (.*)$'
        replacement = rf'- [ ] {task} \1'
        
        # Count matches before replacement
        matches_before = len(re.findall(pattern, content, re.MULTILINE))
        
        if matches_before > 0:
            # Replace [x] with [ ] for this task
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            changes_made += matches_before
            print(f"✓ Unchecked {task} ({matches_before} occurrence(s))")
        else:
            tasks_not_found.append(task)
            print(f"⚠ Task not found or already unchecked: {task}")
    
    # Write the updated content back
    with open('docs/checklist.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total tasks to uncheck: {len(TASKS_TO_UNCHECK)}")
    print(f"Tasks successfully unchecked: {changes_made}")
    print(f"Tasks not found: {len(tasks_not_found)}")
    
    if tasks_not_found:
        print(f"\nTasks not found:")
        for task in tasks_not_found[:10]:  # Show first 10
            print(f"  - {task}")
        if len(tasks_not_found) > 10:
            print(f"  ... and {len(tasks_not_found) - 10} more")
    
    print(f"\nFile updated: docs/checklist.md")
    print(f"Backup available: docs/checklist_backup_20250928_211330.md")

if __name__ == "__main__":
    uncheck_tasks()
