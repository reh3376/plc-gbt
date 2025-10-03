import sys
sys.path.insert(0, '/Users/reh3376/repos/plc-gbt/plc-gbt-stack')

from api.services.file_storage_service import FileStorageService
from api.config.default_file_structure import get_default_folders
from pathlib import Path

# Create service
storage = FileStorageService(
    db_connection_string="postgresql://plc_user:postgres_password@localhost:5432/plc_gbt",
    storage_root=Path("/Users/reh3376/repos/plc-gbt/file-storage")
)

# Get folders to create
folders = get_default_folders()

print(f"Total folders to create: {len(folders)}")
print(f"First few folders: {[f['path'] for f in folders[:10]]}")

# Try to create one folder manually with explicit transaction management
conn = storage.get_connection()
try:
    cur = conn.cursor()
    
    # Count existing
    cur.execute("SELECT COUNT(*) FROM folders")
    count_before = cur.fetchone()[0]
    print(f"Folders before: {count_before}")
    
    # Try to create /projects/active
    parent = storage.get_folder_by_path("/projects")
    print(f"Parent /projects: {parent}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
    conn.close()
