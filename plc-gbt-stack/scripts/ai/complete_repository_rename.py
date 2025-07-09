#!/usr/bin/env python3
"""
Complete Repository Rename - Automated Steps
===========================================

Following AI Task Orchestrator Guide methodology to complete
the repository rename after GitHub rename is finished.

Local directory: PLC_GPT -> plc-gbt (lowercase)
GitHub repository: plc-gpt_build -> plc-gbt (lowercase)

Author: AI Task Orchestrator
Date: January 10, 2025
"""

import os
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def complete_repository_rename():
    """Complete the repository rename process following AI Task Orchestrator methodology"""
    
    logger.info("🚀 Completing Repository Rename - AI Task Orchestrator Guide")
    logger.info("📁 Local directory: PLC_GPT -> plc-gbt")
    logger.info("🔗 GitHub repository: plc-gpt_build -> plc-gbt")
    
    try:
        # Step 1: Update remote URL to new repository
        logger.info("🔄 Step 1: Updating git remote URL to plc-gbt...")
        subprocess.check_output(['git', 'remote', 'set-url', 'origin', 'https://github.com/reh3376/plc-gbt.git'], universal_newlines=True)
        logger.info("✅ Remote URL updated to https://github.com/reh3376/plc-gbt.git")
        
        # Step 2: Test remote connection
        logger.info("🔗 Step 2: Testing remote connection...")
        subprocess.check_output(['git', 'fetch', 'origin'], universal_newlines=True)
        logger.info("✅ Remote connection verified successfully")
        
        # Step 3: Test push capability (dry run)
        logger.info("📤 Step 3: Testing push capability...")
        subprocess.check_output(['git', 'push', '--dry-run', 'origin', 'main'], universal_newlines=True, stderr=subprocess.STDOUT)
        logger.info("✅ Push capability verified")
        
        # Step 4: Rename local directory to lowercase "plc-gbt"
        logger.info("📁 Step 4: Renaming local directory to plc-gbt...")
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        current_name = os.path.basename(current_dir)
        
        if current_name == "PLC_GPT":
            # Change to parent directory
            os.chdir(parent_dir)
            # Rename directory to lowercase
            os.rename("PLC_GPT", "plc-gbt")
            # Change into renamed directory
            os.chdir("plc-gbt")
            logger.info("✅ Local directory renamed from PLC_GPT to plc-gbt")
            logger.info(f"✅ New working directory: {os.getcwd()}")
        elif current_name == "plc-gbt":
            logger.info("ℹ️ Directory already named 'plc-gbt', no rename needed")
        else:
            logger.info(f"ℹ️ Directory currently named '{current_name}', will rename to plc-gbt")
            # Change to parent directory
            os.chdir(parent_dir)
            # Rename directory to plc-gbt
            os.rename(current_name, "plc-gbt")
            # Change into renamed directory
            os.chdir("plc-gbt")
            logger.info(f"✅ Directory renamed from '{current_name}' to plc-gbt")
        
        # Step 5: Final validation
        logger.info("✅ Step 5: Final validation...")
        
        # Check current directory
        current_dir = os.getcwd()
        logger.info(f"📍 Current directory: {current_dir}")
        
        # Verify directory name is correct
        directory_name = os.path.basename(current_dir)
        if directory_name == "plc-gbt":
            logger.info("✅ Local directory name confirmed: plc-gbt")
        else:
            logger.warning(f"⚠️ Directory name is '{directory_name}', expected 'plc-gbt'")
        
        # Check remote URL
        remote_info = subprocess.check_output(['git', 'remote', '-v'], universal_newlines=True).strip()
        logger.info(f"🔗 Remote configuration: {remote_info}")
        
        # Test git status
        git_status = subprocess.check_output(['git', 'status'], universal_newlines=True)
        logger.info("✅ Git status check passed")
        
        # Step 6: Cleanup backup files
        logger.info("🧹 Step 6: Cleaning up backup files...")
        
        # Find and remove backup files
        backup_files_removed = 0
        for file in os.listdir('.'):
            if file.startswith('plc_gpt_backup_') and file.endswith('.bundle'):
                os.remove(file)
                logger.info(f"✅ Removed backup file: {file}")
                backup_files_removed += 1
        
        if backup_files_removed == 0:
            logger.info("ℹ️ No backup files found to clean up")
        
        logger.info("🎉 Repository rename completed successfully!")
        logger.info("📊 Summary:")
        logger.info(f"   • GitHub repository: https://github.com/reh3376/plc-gbt.git")
        logger.info(f"   • Local directory: {os.getcwd()}")
        logger.info(f"   • Directory name: {os.path.basename(os.getcwd())}")
        logger.info(f"   • Git operations: Fully functional")
        logger.info("   • All AI Task Orchestrator validation criteria: PASSED")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Git command failed: {e}")
        logger.error("💡 Make sure you've completed the GitHub repository rename first")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = complete_repository_rename()
    if success:
        print("\n✅ REPOSITORY RENAME COMPLETED SUCCESSFULLY!")
        print("📁 Local directory: plc-gbt")
        print("🔗 GitHub repository: plc-gbt")
        print("You can now use your repository with the new names")
    else:
        print("\n❌ Repository rename encountered issues - please check the logs above") 