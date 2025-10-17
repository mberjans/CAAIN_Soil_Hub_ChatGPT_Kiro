#!/usr/bin/env python3
"""
Script to check implementation status of unchecked tasks
by searching for related code in the codebase.
"""

import os
import re
import subprocess

def find_unchecked_tasks(checklist_path):
    """Find all unchecked tasks in the checklist."""
    unchecked = []
    with open(checklist_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if re.match(r'^\- \[ \] TICKET-', line):
                unchecked.append((line_num, line.strip()))
    return unchecked

def check_if_implemented(task_line):
    """Check if a task might be implemented by searching for related code."""
    # Extract key terms from the task
    # This is a simple heuristic - look for endpoint paths or service names
    
    # Extract API endpoint if present
    endpoint_match = re.search(r'`(/api/[^`]+)`', task_line)
    if endpoint_match:
        endpoint = endpoint_match.group(1)
        # Search for this endpoint in the codebase
        try:
            result = subprocess.run(
                ['grep', '-r', endpoint, 'services/', '--include=*.py'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout:
                return True, f"Found endpoint: {endpoint}"
        except:
            pass
    
    # Extract service name if present
    service_match = re.search(r'TICKET-(\d+)_([a-z-]+)-', task_line)
    if service_match:
        service_name = service_match.group(2)
        service_dir = f"services/{service_name}"
        if os.path.exists(service_dir):
            return True, f"Service directory exists: {service_dir}"
    
    return False, "Not found"

def main():
    checklist_path = 'docs/checklist.md'
    unchecked_tasks = find_unchecked_tasks(checklist_path)
    
    print(f"Found {len(unchecked_tasks)} unchecked tasks\n")
    print("Checking for potentially implemented tasks...\n")
    
    potentially_implemented = []
    
    for line_num, task in unchecked_tasks[:50]:  # Check first 50 for speed
        is_impl, reason = check_if_implemented(task)
        if is_impl:
            potentially_implemented.append((line_num, task, reason))
    
    print(f"\nPotentially implemented but unchecked: {len(potentially_implemented)}\n")
    
    for line_num, task, reason in potentially_implemented:
        print(f"Line {line_num}: {task[:80]}...")
        print(f"  Reason: {reason}\n")

if __name__ == '__main__':
    main()
