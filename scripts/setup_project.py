"""
STEP 0: Setup project structure and dependencies
"""

from pathlib import Path
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_directories():
    """STEP 0.1: Create all necessary directories"""
    dirs = [
        'data/raw',
        'data/processed',
        'data/errors',
        'src/scrapers', #done
        'src/agents',
        'src/tools',
        'src/memory',
        'src/evals',
        'src/embeddings', #done
        'src/graph',
        'ui',
        'scripts',
        'tests',
        'notebooks',
        'docs'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
        
    # STEP 0.2: Create __init__.py files
    init_dirs = [
        'src',
        'src/scrapers',
        'src/agents',
        'src/tools',
        'src/memory',
        'src/evals',
        'src/embeddings',
        'src/graph'
    ]
    
    for dir_path in init_dirs:
        init_file = Path(dir_path) / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            logger.info(f"Created {init_file}")


def check_python_version():
    """STEP 0.3: Verify Python version"""
    if sys.version_info < (3, 10):
        logger.error("Python 3.10+ required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")


def install_dependencies():
    """STEP 0.4: Install dependencies"""
    logger.info("Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
    ])
    logger.info("Dependencies installed")


def main():
    """STEP 0.5: Main setup function"""
    logger.info("Starting project setup...")
    
    check_python_version()
    create_directories()
    
    logger.info("Setup complete! Next steps:")
    logger.info("1. Create .env file with API keys")
    logger.info("2. Run: python scripts/run_day1.py")


if __name__ == "__main__":
    main()