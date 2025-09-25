#!/usr/bin/env python3
"""
Automated script to update all task IDs in docs/checklist.md with corresponding ticket prefixes.
This script maps each task section to its appropriate ticket ID based on the mapping guide.
"""

import re
import os
from pathlib import Path

# Define the mapping from feature sections to ticket IDs
SECTION_TO_TICKET_MAPPING = {
    # Already updated sections (skip these)
    "climate-zone-detection": ["TICKET-001", "TICKET-002"],  # Already done
    "soil-ph-management": ["TICKET-003", "TICKET-004"],      # Already done
    "cover-crop-selection": ["TICKET-013"],                  # Partially done
    
    # Sections to update
    "crop-rotation-planning": ["TICKET-012"],
    "crop-type-filtering": ["TICKET-005"],
    "crop-variety-recommendations": ["TICKET-005"],
    "drought-management": ["TICKET-014"],
    "farm-location-input": ["TICKET-008", "TICKET-010"],
    "fertilizer-application-method": ["TICKET-023"],
    "fertilizer-strategy-optimization": ["TICKET-006"],
    "fertilizer-timing-optimization": ["TICKET-006", "TICKET-023"],
    "fertilizer-type-selection": ["TICKET-023"],
    "micronutrient-management": ["TICKET-016"],
    "nutrient-deficiency-detection": ["TICKET-007"],
    "soil-fertility-assessment": ["TICKET-003", "TICKET-004", "TICKET-017"],
    "runoff-prevention": ["TICKET-024"],
    "soil-tissue-test-integration": ["TICKET-017"],
    "tillage-practice-recommendations": ["TICKET-018"],
    "variety-suitability-explanations": ["TICKET-005"],
    "variety-yield-disease-planting": ["TICKET-005"],
    "weather-impact-analysis": ["TICKET-009"],
    "precision-agriculture-roi": ["TICKET-015"],
    "sustainable-intensification": ["TICKET-019"],
    "government-program-integration": ["TICKET-020"],
    "mobile-field-access": ["TICKET-021"],
    "recommendation-tracking": ["TICKET-022"],
}

# Special mappings for subsections that should use specific tickets
SUBSECTION_SPECIFIC_MAPPING = {
    # Climate Zone Detection (already handled)
    "climate-zone-detection-2": "TICKET-002",  # Auto-detection logic
    "climate-zone-detection-8": "TICKET-002",  # Validation and quality
    "climate-zone-detection-10": "TICKET-011", # Testing
    
    # Soil pH Management (already handled)
    "soil-ph-management-4": "TICKET-004",  # Calculation engine
    "soil-ph-management-6": "TICKET-004",  # Timing recommendations
    "soil-ph-management-7": "TICKET-004",  # Timeline predictions
    "soil-ph-management-10": "TICKET-011", # Testing
    
    # Farm Location Input - UI components
    "farm-location-input-10": "TICKET-010",  # Field Management UI
    "farm-location-input-11": "TICKET-010",  # Mobile-Responsive Design
    
    # Fertilizer sections with multiple tickets
    "fertilizer-timing-optimization-1": "TICKET-006",   # Core timing logic
    "fertilizer-timing-optimization-2": "TICKET-006",   # Integration
    "fertilizer-timing-optimization-3": "TICKET-023",   # Application methods
    
    # Soil Fertility Assessment - lab integration parts
    "soil-fertility-assessment-2": "TICKET-017",  # Lab test integration
    "soil-fertility-assessment-8": "TICKET-017",  # Test result processing
    
    # Testing sections across all features
    "comprehensive-testing": "TICKET-011",
    "testing-and-validation": "TICKET-011",
    "testing-suite": "TICKET-011",
}

def determine_ticket_for_task(section_name, subsection_number=None):
    """
    Determine the appropriate ticket ID for a given task.
    
    Args:
        section_name: The main section name (e.g., 'crop-rotation-planning')
        subsection_number: The subsection number (e.g., '1', '2', etc.)
    
    Returns:
        The appropriate ticket ID (e.g., 'TICKET-012')
    """
    # Check for specific subsection mappings first
    if subsection_number:
        subsection_key = f"{section_name}-{subsection_number}"
        if subsection_key in SUBSECTION_SPECIFIC_MAPPING:
            return SUBSECTION_SPECIFIC_MAPPING[subsection_key]
    
    # Check for testing-related sections
    if any(test_keyword in section_name.lower() for test_keyword in ['testing', 'validation', 'test-suite']):
        return "TICKET-011"
    
    # Check for mobile-related sections
    if 'mobile' in section_name.lower():
        return "TICKET-021"
    
    # Use main section mapping
    if section_name in SECTION_TO_TICKET_MAPPING:
        tickets = SECTION_TO_TICKET_MAPPING[section_name]
        return tickets[0]  # Use first ticket as default
    
    # Default fallback
    return "TICKET-XXX"

def process_checklist_file(file_path):
    """
    Process the checklist file and update task IDs with ticket prefixes.
    
    Args:
        file_path: Path to the docs/checklist.md file
    """
    print(f"Processing file: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = 0
    
    # Pattern to match section headers: ### section-name-number. Title
    section_pattern = r'^### ([a-z-]+)-(\d+)\. (.+)$'
    
    # Pattern to match task items: - [x] section-name-number.subnumber Task description
    task_pattern = r'^(\s*)- \[([x\s\-/])\] ([a-z-]+)-(\d+)\.(\d+(?:\.\d+)*) (.+)$'
    
    lines = content.split('\n')
    current_section = None
    current_section_number = None
    
    for i, line in enumerate(lines):
        # Check for section headers
        section_match = re.match(section_pattern, line)
        if section_match:
            current_section = section_match.group(1)
            current_section_number = section_match.group(2)
            section_title = section_match.group(3)
            
            # Skip already updated sections
            if (current_section in ["climate-zone-detection", "soil-ph-management"] or 
                line.startswith("### TICKET-")):
                continue
            
            # Update section header
            ticket_id = determine_ticket_for_task(current_section, current_section_number)
            new_header = f"### {ticket_id}_{current_section}-{current_section_number}. {section_title}"
            lines[i] = new_header
            changes_made += 1
            print(f"Updated section: {current_section}-{current_section_number} → {ticket_id}")
            continue
        
        # Check for task items
        task_match = re.match(task_pattern, line)
        if task_match and current_section:
            indent = task_match.group(1)
            status = task_match.group(2)
            task_section = task_match.group(3)
            section_num = task_match.group(4)
            task_num = task_match.group(5)
            description = task_match.group(6)
            
            # Skip already updated tasks
            if line.strip().startswith("- [") and "TICKET-" in line:
                continue
            
            # Determine appropriate ticket
            ticket_id = determine_ticket_for_task(task_section, section_num)
            
            # Update task line
            new_task = f"{indent}- [{status}] {ticket_id}_{task_section}-{section_num}.{task_num} {description}"
            lines[i] = new_task
            changes_made += 1
    
    # Write the updated content back to file
    updated_content = '\n'.join(lines)
    
    # Create backup
    backup_path = f"{file_path}.backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup: {backup_path}")
    
    # Write updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Processing complete! Made {changes_made} changes.")
    return changes_made

def validate_updates(file_path):
    """
    Validate that the updates were applied correctly.
    
    Args:
        file_path: Path to the updated checklist file
    """
    print("\n🔍 Validating updates...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count sections and tasks with ticket prefixes
    ticket_sections = len(re.findall(r'^### TICKET-\d+_', content, re.MULTILINE))
    ticket_tasks = len(re.findall(r'^\s*- \[[x\s\-/]\] TICKET-\d+_', content, re.MULTILINE))
    
    # Count sections and tasks without ticket prefixes (should be minimal)
    non_ticket_sections = len(re.findall(r'^### [a-z-]+-\d+\.', content, re.MULTILINE))
    non_ticket_tasks = len(re.findall(r'^\s*- \[[x\s\-/]\] [a-z-]+-\d+\.', content, re.MULTILINE))
    
    print(f"✅ Sections with ticket prefixes: {ticket_sections}")
    print(f"✅ Tasks with ticket prefixes: {ticket_tasks}")
    print(f"⚠️  Sections without ticket prefixes: {non_ticket_sections}")
    print(f"⚠️  Tasks without ticket prefixes: {non_ticket_tasks}")
    
    if non_ticket_sections == 0 and non_ticket_tasks == 0:
        print("🎉 All sections and tasks successfully updated with ticket prefixes!")
    else:
        print("⚠️  Some sections or tasks may need manual review.")
    
    return ticket_sections, ticket_tasks, non_ticket_sections, non_ticket_tasks

def main():
    """Main execution function."""
    print("🚀 Starting automated task ID update process...")
    
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    checklist_path = project_root / "docs" / "checklist.md"
    
    if not checklist_path.exists():
        print(f"❌ Error: Checklist file not found at {checklist_path}")
        return
    
    # Process the file
    changes = process_checklist_file(checklist_path)
    
    # Validate the results
    validate_updates(checklist_path)
    
    print(f"\n✅ Script completed successfully!")
    print(f"📊 Total changes made: {changes}")
    print(f"📁 Updated file: {checklist_path}")
    print(f"💾 Backup created: {checklist_path}.backup")
    
    print("\n📋 Next steps:")
    print("1. Review the updated docs/checklist.md file")
    print("2. Verify ticket-task mappings are correct")
    print("3. Update any project management tools with new task IDs")
    print("4. Inform AI coding agents of the new ID format")

if __name__ == "__main__":
    main()
