#!/usr/bin/env python3
"""
Script to search for 156 incorrectly marked tasks in AI coder log files
and identify which AI coder was responsible for each task.
"""

import re
import csv
from typing import Dict, List, Tuple, Optional

# List of all 156 incorrectly marked tasks
TASKS = [
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
    
    # TICKET-007: Nutrient Deficiency Detection (21 selected tasks from 42 total)
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

    # Total tasks: 135 (phantom) + 21 (TICKET-007) = 156 tasks exactly
]

def extract_ai_coder_from_line(line: str) -> Optional[str]:
    """Extract AI coder name from execution mode line."""
    patterns = {
        'Gemini': r'🔮 Using Gemini execution mode',
        'Qwen': r'🤖 Using Qwen execution mode', 
        'Codex': r'🤖 Using Codex execution mode',
        'Cursor': r'🎯 Using Cursor execution mode',
        'Crush': r'🔥 Using Crush execution mode',
        'Rovodev': r'🚀 Using Rovodev execution mode',
        'OpenCode': r'🔧 Using OpenCode execution mode'
    }
    
    for coder, pattern in patterns.items():
        if re.search(pattern, line):
            return coder
    return None

def search_task_in_file(task: str, filepath: str) -> Tuple[bool, Optional[str], List[str]]:
    """
    Search for a task in a log file.
    Returns: (found, ai_coder, evidence_lines)
    """
    found = False
    ai_coder = None
    evidence_lines = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Search for task mentions
        for i, line in enumerate(lines):
            if task in line:
                found = True
                evidence_lines.append(f"Line {i+1}: {line.strip()}")

                # Look backwards for AI coder execution mode within 1000 lines (broader search)
                for j in range(max(0, i-1000), i):
                    coder = extract_ai_coder_from_line(lines[j])
                    if coder:
                        ai_coder = coder
                        evidence_lines.append(f"Line {j+1}: {lines[j].strip()}")
                        break

                # If not found backwards, look forwards within 100 lines
                if not ai_coder:
                    for j in range(i+1, min(len(lines), i+100)):
                        coder = extract_ai_coder_from_line(lines[j])
                        if coder:
                            ai_coder = coder
                            evidence_lines.append(f"Line {j+1}: {lines[j].strip()}")
                            break

                # Only need first occurrence
                break

    except Exception as e:
        evidence_lines.append(f"Error reading file: {e}")

    return found, ai_coder, evidence_lines

def main():
    """Main function to search all tasks and generate CSV report."""
    results = []
    
    log_files = ['AI_coder_log_1.txt', 'AI_coder_log_2.txt']
    
    print(f"Searching for {len(TASKS)} tasks in {len(log_files)} log files...")
    
    for i, task in enumerate(TASKS, 1):
        print(f"Processing task {i}/{len(TASKS)}: {task}")
        
        found_in_log1, ai_coder_log1, evidence_log1 = search_task_in_file(task, log_files[0])
        found_in_log2, ai_coder_log2, evidence_log2 = search_task_in_file(task, log_files[1])
        
        # Determine final AI coder
        ai_coder = ai_coder_log1 or ai_coder_log2 or "NONE"
        found = found_in_log1 or found_in_log2

        # Debug output for tasks that have AI coder detected
        if ai_coder != "NONE":
            print(f"  -> Found AI coder {ai_coder} for task {task}")
        
        # Combine evidence
        all_evidence = evidence_log1 + evidence_log2
        evidence_summary = "; ".join(all_evidence[:3])  # Limit evidence length
        
        results.append({
            'Task': task,
            'Found_in_Logs': 'YES' if found else 'NO',
            'AI_Coder': ai_coder,
            'Found_in_Log1': 'YES' if found_in_log1 else 'NO',
            'Found_in_Log2': 'YES' if found_in_log2 else 'NO',
            'Evidence': evidence_summary
        })
    
    # Write CSV file
    csv_filename = 'wrongly_checked_tasks_analysis.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Task', 'Found_in_Logs', 'AI_Coder', 'Found_in_Log1', 'Found_in_Log2', 'Evidence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    # Print summary
    total_tasks = len(results)
    found_tasks = sum(1 for r in results if r['Found_in_Logs'] == 'YES')
    ai_coder_counts = {}
    
    for result in results:
        coder = result['AI_Coder']
        ai_coder_counts[coder] = ai_coder_counts.get(coder, 0) + 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Total tasks analyzed: {total_tasks}")
    print(f"Tasks found in logs: {found_tasks}")
    print(f"Tasks NOT found in logs: {total_tasks - found_tasks}")
    print(f"\nAI Coder breakdown:")
    for coder, count in sorted(ai_coder_counts.items()):
        print(f"  {coder}: {count} tasks")
    
    print(f"\nResults saved to: {csv_filename}")

if __name__ == "__main__":
    main()
