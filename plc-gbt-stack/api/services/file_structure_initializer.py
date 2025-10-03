#!/usr/bin/env python3
"""
File Structure Initialization Service
Creates the default folder structure and README files
"""

import logging
from typing import Any

from api.config.default_file_structure import (
    ROOT_README,
    get_category_readme,
    get_default_folders,
)
from api.services.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


class FileStructureInitializer:
    """
    Initializes default file structure in the database and filesystem
    """

    def __init__(self, storage_service: FileStorageService):
        """
        Initialize with storage service
        
        Args:
            storage_service: FileStorageService instance
        """
        self.storage_service = storage_service

    def initialize_structure(self, force: bool = False) -> dict[str, Any]:
        """
        Initialize default file structure
        
        Args:
            force: If True, recreate structure even if it exists
            
        Returns:
            Initialization result summary
        """
        logger.info("Initializing default file structure...")

        created_folders = 0
        created_files = 0
        skipped = 0
        errors = []

        try:
            # Get flattened folder structure
            folders = get_default_folders()

            # Create folders in order (parents before children)
            for folder_def in folders:
                try:
                    # Skip root folder (already exists)
                    if folder_def["path"] == "/":
                        # Create root README
                        try:
                            self._create_readme(
                                folder_path="/",
                                content=ROOT_README,
                                filename="README.md"
                            )
                            created_files += 1
                            logger.info("Created root README.md")
                        except Exception as e:
                            logger.warning(f"Could not create root README: {e}")
                        continue

                    # Check if folder exists
                    existing = self.storage_service.get_folder_by_path(folder_def["path"])

                    if existing and not force:
                        logger.debug(f"Folder already exists: {folder_def['path']}")
                        skipped += 1
                        continue

                    # Create folder
                    folder = self.storage_service.create_folder(
                        name=folder_def["name"],
                        parent_path=folder_def["parent_path"],
                        category_name=folder_def.get("category"),
                        created_by="system",
                        description=folder_def.get("description"),
                        metadata={
                            "icon": folder_def.get("icon"),
                            "color": folder_def.get("color"),
                            "is_default": True,
                        }
                    )

                    created_folders += 1
                    logger.info(f"Created folder: {folder_def['path']}")

                    # Create README if specified
                    if folder_def.get("readme"):
                        try:
                            self._create_readme(
                                folder_path=folder_def["path"],
                                content=folder_def["readme"],
                                filename="README.md"
                            )
                            created_files += 1
                            logger.info(f"Created README in {folder_def['path']}")
                        except Exception as e:
                            logger.warning(f"Could not create README in {folder_def['path']}: {e}")

                    # Create category README if applicable
                    elif folder_def.get("category"):
                        category_readme = get_category_readme(folder_def["category"])
                        if category_readme:
                            try:
                                self._create_readme(
                                    folder_path=folder_def["path"],
                                    content=category_readme,
                                    filename="README.md"
                                )
                                created_files += 1
                                logger.info(f"Created category README in {folder_def['path']}")
                            except Exception as e:
                                logger.warning(f"Could not create category README in {folder_def['path']}: {e}")

                except Exception as e:
                    error_msg = f"Error creating folder {folder_def.get('path', 'unknown')}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Create .gitkeep files in empty system folders
            self._create_gitkeep_files()

            result = {
                "success": len(errors) == 0,
                "folders_created": created_folders,
                "files_created": created_files,
                "folders_skipped": skipped,
                "errors": errors,
                "message": f"Created {created_folders} folders and {created_files} files"
            }

            logger.info(f"Initialization complete: {result['message']}")
            return result

        except Exception as e:
            error_msg = f"Fatal error during initialization: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "folders_created": created_folders,
                "files_created": created_files,
                "folders_skipped": skipped,
                "errors": errors + [error_msg],
                "message": error_msg
            }

    def _create_readme(self, folder_path: str, content: str, filename: str = "README.md"):
        """
        Create a README file in a folder
        
        Args:
            folder_path: Target folder path
            content: README content
            filename: README filename
        """
        # Check if README already exists
        existing_files = self.storage_service.list_files(
            folder_path=folder_path,
            limit=100
        )

        for file in existing_files:
            if file['name'].lower() == filename.lower():
                logger.debug(f"README already exists in {folder_path}")
                return

        # Upload README
        self.storage_service.upload_file(
            file_content=content.encode('utf-8'),
            filename=filename,
            folder_path=folder_path,
            category_name="documentation",
            created_by="system",
            description=f"Default README for {folder_path}",
            tags=["readme", "documentation", "default"],
            metadata={"auto_generated": True, "version": "1.0"}
        )

    def _create_gitkeep_files(self):
        """
        Create .gitkeep files in empty system folders
        This ensures empty folders are tracked in version control
        """
        gitkeep_content = b"# This file ensures the folder is tracked in version control\n"

        # Get all system folders
        folders = get_default_folders()

        for folder_def in folders:
            if folder_def.get("is_system") and folder_def["path"] != "/":
                # Check if folder has any files
                existing_files = self.storage_service.list_files(
                    folder_path=folder_def["path"],
                    limit=1
                )

                # Only create .gitkeep if folder is empty
                if not existing_files:
                    try:
                        self.storage_service.upload_file(
                            file_content=gitkeep_content,
                            filename=".gitkeep",
                            folder_path=folder_def["path"],
                            created_by="system",
                            description="Placeholder file for version control",
                            tags=["system", "gitkeep"],
                            metadata={"hidden": True}
                        )
                        logger.debug(f"Created .gitkeep in {folder_def['path']}")
                    except Exception as e:
                        logger.debug(f"Could not create .gitkeep in {folder_def['path']}: {e}")

    def verify_structure(self) -> dict[str, Any]:
        """
        Verify that the default structure exists
        
        Returns:
            Verification result with missing folders/files
        """
        folders = get_default_folders()
        missing_folders = []
        existing_folders = []

        for folder_def in folders:
            existing = self.storage_service.get_folder_by_path(folder_def["path"])
            if existing:
                existing_folders.append(folder_def["path"])
            else:
                missing_folders.append(folder_def["path"])

        is_complete = len(missing_folders) == 0

        return {
            "is_complete": is_complete,
            "total_folders": len(folders),
            "existing_folders": len(existing_folders),
            "missing_folders": missing_folders,
            "completion_percentage": (len(existing_folders) / len(folders)) * 100 if folders else 0
        }

    def reset_structure(self) -> dict[str, Any]:
        """
        Reset the entire file structure (dangerous operation!)
        This will soft-delete all existing folders and recreate the default structure
        
        Returns:
            Reset operation result
        """
        logger.warning("Resetting file structure - this will soft-delete all folders!")

        # TODO: Implement soft-delete all folders
        # For now, just reinitialize with force=True
        return self.initialize_structure(force=True)


def initialize_default_structure(storage_service: FileStorageService) -> dict[str, Any]:
    """
    Convenience function to initialize default structure
    
    Args:
        storage_service: FileStorageService instance
        
    Returns:
        Initialization result
    """
    initializer = FileStructureInitializer(storage_service)
    return initializer.initialize_structure()

