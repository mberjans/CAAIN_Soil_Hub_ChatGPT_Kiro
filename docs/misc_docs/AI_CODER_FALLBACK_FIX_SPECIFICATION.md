# AI Coder Fallback Logic Fix Specification

## Problem Statement

The current AI coder orchestration system has flawed fallback logic that:
1. **Checks historical failures** from previous AI coder sessions when the current AI coder fails
2. **Uses stale data** (e.g., old API quota limits) to make current availability decisions
3. **Doesn't test current availability** of preceding AI coders before falling back to downstream coders
4. **Conflates different failure types** (infrastructure issues vs. API limits)

### Example of Current Flawed Behavior:
```
1. Qwen fails (missing directory) → Current failure
2. System checks Gemini's old logs → Historical data
3. Finds Gemini had API quota exceeded yesterday → Stale information
4. Declares both unavailable → Incorrect decision
5. Doesn't try to fix Qwen's directory issue → Missed opportunity
6. Doesn't test if Gemini's quota has reset → Missed opportunity
```

## Required Fix

### New Fallback Logic Flow

When an AI coder fails, the system should:

1. **Test ALL preceding AI coders** (from the beginning of the priority list) for current availability
2. **Only after all preceding coders fail** the current availability test, proceed to the next downstream coder
3. **Use real-time availability testing**, not historical log analysis
4. **Attempt simple fixes** before declaring an AI coder unavailable

### Priority Order (from `ai_coder_fallback_config.json`):
```
codex → claude → rovodev → gemini → qwen → ccr → opencode → cursor → crush → droid → amp → cline → copilot → iflow → auggie
```

### Correct Fallback Behavior Examples:

#### Example 1: Qwen Fails
```
Current AI Coder: qwen (position 5)
Failure: Missing directory

Correct Action:
1. Test codex (position 1) - Is it available NOW?
2. Test claude (position 2) - Is it available NOW?
3. Test rovodev (position 3) - Is it available NOW?
4. Test gemini (position 4) - Is it available NOW?
5. If any of 1-4 are available → Use that coder
6. If all of 1-4 fail → Try ccr (position 6)
```

#### Example 2: Gemini Fails with API Quota
```
Current AI Coder: gemini (position 4)
Failure: API quota exceeded

Correct Action:
1. Test codex (position 1) - Is it available NOW?
2. Test claude (position 2) - Is it available NOW?
3. Test rovodev (position 3) - Is it available NOW?
4. If any of 1-3 are available → Use that coder
5. If all of 1-3 fail → Try qwen (position 5)
```

## Implementation Requirements

### 1. Real-Time Availability Testing

Replace historical log checking with real-time availability tests:

```python
def test_ai_coder_availability(coder_name: str, coder_config: dict) -> tuple[bool, str]:
    """
    Test if an AI coder is currently available.
    
    Returns:
        (is_available, failure_reason)
    """
    # Test 1: Check if required directories exist
    if not check_directories_exist(coder_name):
        try:
            create_required_directories(coder_name)
        except Exception as e:
            return False, f"Directory creation failed: {e}"
    
    # Test 2: Check if command is available
    if not check_command_available(coder_config["command"]):
        return False, f"Command not found: {coder_config['command']}"
    
    # Test 3: Quick API test (if applicable)
    if requires_api_test(coder_name):
        try:
            result = quick_api_test(coder_name, timeout=10)
            if not result.success:
                return False, f"API test failed: {result.error}"
        except TimeoutError:
            return False, "API test timeout"
    
    return True, ""
```

### 2. Fallback Selection Algorithm

```python
def select_next_ai_coder(
    current_coder: str,
    current_failure_reason: str,
    ai_coder_priority_order: list
) -> Optional[str]:
    """
    Select the next available AI coder using correct fallback logic.
    
    Algorithm:
    1. Find current coder's position in priority list
    2. Test ALL coders BEFORE current position (from beginning)
    3. If any preceding coder is available, use it
    4. If all preceding coders fail, try next downstream coder
    5. Repeat until an available coder is found or list is exhausted
    """
    # Find current position
    current_index = find_coder_index(current_coder, ai_coder_priority_order)
    
    # Test all preceding coders (positions 0 to current_index-1)
    for i in range(current_index):
        coder_config = ai_coder_priority_order[i]
        if not coder_config["enabled"]:
            continue
            
        is_available, reason = test_ai_coder_availability(
            coder_config["name"],
            coder_config
        )
        
        if is_available:
            logger.info(f"✅ Found available preceding AI coder: {coder_config['name']} (position {i+1})")
            return coder_config["name"]
        else:
            logger.debug(f"❌ Preceding AI coder {coder_config['name']} unavailable: {reason}")
    
    # All preceding coders failed, try next downstream coder
    for i in range(current_index + 1, len(ai_coder_priority_order)):
        coder_config = ai_coder_priority_order[i]
        if not coder_config["enabled"]:
            continue
            
        is_available, reason = test_ai_coder_availability(
            coder_config["name"],
            coder_config
        )
        
        if is_available:
            logger.info(f"✅ Found available downstream AI coder: {coder_config['name']} (position {i+1})")
            return coder_config["name"]
        else:
            logger.debug(f"❌ Downstream AI coder {coder_config['name']} unavailable: {reason}")
    
    # No available AI coders found
    logger.error("❌ No available AI coders found in entire priority list")
    return None
```

### 3. Remove Historical Log Checking

**DELETE or DISABLE** any code that:
- Reads previous AI coder log files to determine availability
- Checks for "quota exceeded" or "usage limit" messages in old logs
- Uses `failed_ai_coders` list from `fallback_state` for availability decisions

**KEEP** historical logging only for:
- Analytics and reporting
- Pattern detection (not availability decisions)
- Debugging purposes

### 4. Update Fallback State Management

```python
def update_fallback_state(
    new_coder: str,
    previous_coder: str,
    failure_reason: str,
    config_path: str
):
    """
    Update fallback state with current information only.
    
    DO NOT store:
    - Historical failures
    - Old API quota information
    - Stale availability data
    
    DO store:
    - Current active AI coder
    - Timestamp of last switch
    - Reason for current switch (for logging only)
    """
    config = load_config(config_path)
    
    config["fallback_state"] = {
        "current_ai_coder": new_coder,
        "fallback_active": True,
        "previous_ai_coder": previous_coder,
        "last_fallback_time": datetime.now().isoformat(),
        "last_failure_reason": failure_reason,  # For logging only
        "fallback_count": config["fallback_state"].get("fallback_count", 0) + 1
    }
    
    # Remove failed_ai_coders list - it's misleading
    # Each fallback should test availability fresh
    
    save_config(config, config_path)
```

## Testing Requirements

### Test Case 1: Qwen Fails, Codex Available
```
Initial: qwen (position 5)
Failure: Missing directory
Expected: Switch to codex (position 1)
```

### Test Case 2: Gemini Fails, All Preceding Unavailable
```
Initial: gemini (position 4)
Failure: API quota
Codex: Unavailable (command not found)
Claude: Unavailable (API error)
Rovodev: Unavailable (timeout)
Expected: Switch to qwen (position 5)
```

### Test Case 3: Qwen Fails, Claude Available
```
Initial: qwen (position 5)
Failure: API error
Codex: Unavailable
Claude: Available
Expected: Switch to claude (position 2), NOT rovodev or gemini
```

## Files to Modify

The fix should be implemented in:
```
/Users/Mark/Software/full_automation_of_coding_clean_five_agents/ai_coder.py
```

Specifically, look for functions related to:
- `handle_fallback()`
- `check_usage_limit()`
- `select_next_ai_coder()`
- `test_ai_coder_availability()`

## Summary

**Key Principle**: When an AI coder fails, always test ALL preceding AI coders from the beginning of the priority list for CURRENT availability before falling back to downstream coders. Never use historical log data to make availability decisions.

