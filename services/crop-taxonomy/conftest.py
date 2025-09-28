import sys
from pathlib import Path

# Add the 'src' directory to sys.path for test discovery
# This allows absolute imports from 'src' in tests
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "crop-taxonomy" / "src"))
