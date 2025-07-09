#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features
"""

from enum import Enum
from typing import List, Set, Dict, Any, Optional
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


class Role(Enum):
    """User roles in the PLC-GPT system."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    AUDITOR = "auditor"
    GUEST = "guest"


class Permission(Enum):
    """Permissions in the PLC-GPT system."""
    # Data Access Permissions
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    EXPORT_DATA = "export_data"
    
    # Query Permissions
    EXECUTE_QUERIES = "execute_queries"
    CREATE_QUERIES = "create_queries"
    MODIFY_QUERIES = "modify_queries"
    DELETE_QUERIES = "delete_queries"
    
    # User Management Permissions
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    MODIFY_USERS = "modify_users"
    DELETE_USERS = "delete_users"
    
    # System Permissions
    VIEW_METRICS = "view_metrics"
    MANAGE_SYSTEM = "manage_system"
    CONFIGURE_SYSTEM = "configure_system"
    VIEW_LOGS = "view_logs"
    MANAGE_LOGS = "manage_logs"
    
    # Cache Permissions
    MANAGE_CACHE = "manage_cache"
    VIEW_CACHE_STATS = "view_cache_stats"
    INVALIDATE_CACHE = "invalidate_cache"
    
    # API Permissions
    ACCESS_API = "access_api"
    ADMIN_API = "admin_api"
    DEVELOPER_API = "developer_api"
    
    # Authentication Permissions
    MANAGE_TOKENS = "manage_tokens"
    REVOKE_TOKENS = "revoke_tokens"
    VIEW_AUTH_LOGS = "view_auth_logs"
    
    # Monitoring Permissions
    VIEW_MONITORING = "view_monitoring"
    CONFIGURE_MONITORING = "configure_monitoring"
    EXPORT_METRICS = "export_metrics"


@dataclass
class RoleDefinition:
    """Definition of a role with its permissions and description."""
    role: Role
    permissions: Set[Permission]
    description: str
    hierarchy_level: int  # Higher number = more privileges


class RBACManager:
    """
    Role-Based Access Control Manager.
    
    Features:
    - Role and permission management
    - Hierarchical permission inheritance
    - Permission checking and validation
    - Dynamic role assignment
    - Audit logging for access control
    """
    
    def __init__(self, settings=None):
        """
        Initialize RBAC Manager.
        
        Args:
            settings: Enterprise settings instance
        """
        self.settings = settings
        self.role_definitions = self._define_roles()
        self.role_hierarchy = self._build_role_hierarchy()
        
        logger.info("RBAC Manager initialized",
                   roles_count=len(self.role_definitions),
                   permissions_count=len(Permission))
    
    def _define_roles(self) -> Dict[Role, RoleDefinition]:
        """Define all roles and their permissions."""
        return {
            Role.GUEST: RoleDefinition(
                role=Role.GUEST,
                permissions={
                    Permission.ACCESS_API,
                },
                description="Guest user with minimal access",
                hierarchy_level=1
            ),
            
            Role.USER: RoleDefinition(
                role=Role.USER,
                permissions={
                    Permission.READ_DATA,
                    Permission.EXECUTE_QUERIES,
                    Permission.CREATE_QUERIES,
                    Permission.ACCESS_API,
                    Permission.VIEW_CACHE_STATS,
                },
                description="Standard user with query and read access",
                hierarchy_level=2
            ),
            
            Role.DEVELOPER: RoleDefinition(
                role=Role.DEVELOPER,
                permissions={
                    Permission.READ_DATA,
                    Permission.WRITE_DATA,
                    Permission.EXECUTE_QUERIES,
                    Permission.CREATE_QUERIES,
                    Permission.MODIFY_QUERIES,
                    Permission.DELETE_QUERIES,
                    Permission.ACCESS_API,
                    Permission.DEVELOPER_API,
                    Permission.VIEW_METRICS,
                    Permission.VIEW_CACHE_STATS,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_MONITORING,
                    Permission.EXPORT_DATA,
                },
                description="Developer with extended access to system features",
                hierarchy_level=3
            ),
            
            Role.AUDITOR: RoleDefinition(
                role=Role.AUDITOR,
                permissions={
                    Permission.READ_DATA,
                    Permission.VIEW_USERS,
                    Permission.VIEW_METRICS,
                    Permission.VIEW_LOGS,
                    Permission.VIEW_AUTH_LOGS,
                    Permission.VIEW_CACHE_STATS,
                    Permission.VIEW_MONITORING,
                    Permission.EXPORT_METRICS,
                    Permission.ACCESS_API,
                },
                description="Auditor with read-only access to logs and metrics",
                hierarchy_level=3
            ),
            
            Role.ADMIN: RoleDefinition(
                role=Role.ADMIN,
                permissions=set(Permission),  # All permissions
                description="Administrator with full system access",
                hierarchy_level=4
            ),
        }
    
    def _build_role_hierarchy(self) -> Dict[Role, int]:
        """Build role hierarchy mapping."""
        return {
            role_def.role: role_def.hierarchy_level
            for role_def in self.role_definitions.values()
        }
    
    def has_permission(self, user_role: Role, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            user_role: User's role
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        try:
            role_def = self.role_definitions.get(user_role)
            if not role_def:
                logger.warning("Unknown role", role=user_role)
                return False
            
            has_perm = permission in role_def.permissions
            
            logger.debug("Permission check",
                        role=user_role.value,
                        permission=permission.value,
                        granted=has_perm)
            
            return has_perm
            
        except Exception as e:
            logger.error("Error checking permission",
                        role=user_role,
                        permission=permission,
                        error=str(e))
            return False
    
    def has_any_permission(self, user_role: Role, permissions: List[Permission]) -> bool:
        """
        Check if a role has any of the specified permissions.
        
        Args:
            user_role: User's role
            permissions: List of permissions to check
            
        Returns:
            True if role has any permission, False otherwise
        """
        return any(self.has_permission(user_role, perm) for perm in permissions)
    
    def has_all_permissions(self, user_role: Role, permissions: List[Permission]) -> bool:
        """
        Check if a role has all specified permissions.
        
        Args:
            user_role: User's role
            permissions: List of permissions to check
            
        Returns:
            True if role has all permissions, False otherwise
        """
        return all(self.has_permission(user_role, perm) for perm in permissions)
    
    def get_role_permissions(self, user_role: Role) -> Set[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            user_role: User's role
            
        Returns:
            Set of permissions for the role
        """
        role_def = self.role_definitions.get(user_role)
        if not role_def:
            logger.warning("Unknown role", role=user_role)
            return set()
        
        return role_def.permissions.copy()
    
    def get_user_role(self, email: str, default_role: Role = Role.USER) -> Role:
        """
        Determine user role based on email and settings.
        
        Args:
            email: User's email address
            default_role: Default role if not specified
            
        Returns:
            User's role
        """
        if not self.settings:
            return default_role
        
        email = email.lower().strip()
        
        # Check for admin users
        if self.settings.is_admin_user(email):
            logger.info("Admin role assigned", email=email)
            return Role.ADMIN
        
        # Check for developer users
        if self.settings.is_developer_user(email):
            logger.info("Developer role assigned", email=email)
            return Role.DEVELOPER
        
        # Use configured default role
        default_role_str = getattr(self.settings, 'default_user_role', 'user')
        try:
            default_role = Role(default_role_str)
        except ValueError:
            logger.warning("Invalid default role in settings", 
                          role=default_role_str, 
                          fallback=default_role.value)
        
        logger.info("Default role assigned", email=email, role=default_role.value)
        return default_role
    
    def is_role_higher_than(self, role1: Role, role2: Role) -> bool:
        """
        Check if role1 has higher privileges than role2.
        
        Args:
            role1: First role
            role2: Second role
            
        Returns:
            True if role1 is higher than role2
        """
        level1 = self.role_hierarchy.get(role1, 0)
        level2 = self.role_hierarchy.get(role2, 0)
        return level1 > level2
    
    def can_manage_user(self, manager_role: Role, target_role: Role) -> bool:
        """
        Check if a manager role can manage a target role.
        
        Args:
            manager_role: Role of the manager
            target_role: Role of the target user
            
        Returns:
            True if manager can manage target
        """
        # Admins can manage anyone
        if manager_role == Role.ADMIN:
            return True
        
        # Users can only manage users with lower or equal hierarchy
        return self.is_role_higher_than(manager_role, target_role) or manager_role == target_role
    
    def get_accessible_roles(self, user_role: Role) -> List[Role]:
        """
        Get list of roles that a user can manage.
        
        Args:
            user_role: User's role
            
        Returns:
            List of manageable roles
        """
        user_level = self.role_hierarchy.get(user_role, 0)
        accessible_roles = []
        
        for role, level in self.role_hierarchy.items():
            if user_role == Role.ADMIN or level <= user_level:
                accessible_roles.append(role)
        
        return accessible_roles
    
    def validate_role_transition(self, current_role: Role, new_role: Role, modifier_role: Role) -> bool:
        """
        Validate if a role transition is allowed.
        
        Args:
            current_role: Current user role
            new_role: Proposed new role
            modifier_role: Role of the user making the change
            
        Returns:
            True if transition is allowed
        """
        # Check if modifier can manage both roles
        can_manage_current = self.can_manage_user(modifier_role, current_role)
        can_manage_new = self.can_manage_user(modifier_role, new_role)
        
        is_valid = can_manage_current and can_manage_new
        
        logger.info("Role transition validation",
                   current_role=current_role.value,
                   new_role=new_role.value,
                   modifier_role=modifier_role.value,
                   is_valid=is_valid)
        
        return is_valid
    
    def get_role_description(self, role: Role) -> str:
        """
        Get description for a role.
        
        Args:
            role: Role to describe
            
        Returns:
            Role description
        """
        role_def = self.role_definitions.get(role)
        return role_def.description if role_def else f"Unknown role: {role.value}"
    
    def get_permission_description(self, permission: Permission) -> str:
        """
        Get description for a permission.
        
        Args:
            permission: Permission to describe
            
        Returns:
            Permission description
        """
        descriptions = {
            Permission.READ_DATA: "Read access to PLC data and projects",
            Permission.WRITE_DATA: "Write access to PLC data and projects",
            Permission.DELETE_DATA: "Delete access to PLC data and projects",
            Permission.EXPORT_DATA: "Export PLC data and reports",
            Permission.EXECUTE_QUERIES: "Execute queries against the knowledge graph",
            Permission.CREATE_QUERIES: "Create new queries",
            Permission.MODIFY_QUERIES: "Modify existing queries",
            Permission.DELETE_QUERIES: "Delete queries",
            Permission.MANAGE_USERS: "Full user management capabilities",
            Permission.VIEW_USERS: "View user information",
            Permission.CREATE_USERS: "Create new users",
            Permission.MODIFY_USERS: "Modify user information",
            Permission.DELETE_USERS: "Delete users",
            Permission.VIEW_METRICS: "View system performance metrics",
            Permission.MANAGE_SYSTEM: "Manage system configuration",
            Permission.CONFIGURE_SYSTEM: "Configure system settings",
            Permission.VIEW_LOGS: "View system logs",
            Permission.MANAGE_LOGS: "Manage log configuration",
            Permission.MANAGE_CACHE: "Manage cache configuration",
            Permission.VIEW_CACHE_STATS: "View cache statistics",
            Permission.INVALIDATE_CACHE: "Invalidate cache entries",
            Permission.ACCESS_API: "Basic API access",
            Permission.ADMIN_API: "Administrative API access",
            Permission.DEVELOPER_API: "Developer API access",
            Permission.MANAGE_TOKENS: "Manage authentication tokens",
            Permission.REVOKE_TOKENS: "Revoke user tokens",
            Permission.VIEW_AUTH_LOGS: "View authentication logs",
            Permission.VIEW_MONITORING: "View monitoring dashboard",
            Permission.CONFIGURE_MONITORING: "Configure monitoring settings",
            Permission.EXPORT_METRICS: "Export metrics and reports",
        }
        
        return descriptions.get(permission, f"Unknown permission: {permission.value}")
    
    def get_roles_summary(self) -> Dict[str, Any]:
        """
        Get summary of all roles and their permissions.
        
        Returns:
            Dictionary with roles summary
        """
        summary = {}
        
        for role, role_def in self.role_definitions.items():
            summary[role.value] = {
                "description": role_def.description,
                "hierarchy_level": role_def.hierarchy_level,
                "permissions_count": len(role_def.permissions),
                "permissions": [perm.value for perm in role_def.permissions]
            }
        
        return summary
    
    def audit_permission_check(self, user_id: str, user_role: Role, permission: Permission, granted: bool):
        """
        Log permission check for audit purposes.
        
        Args:
            user_id: User ID
            user_role: User's role
            permission: Permission checked
            granted: Whether permission was granted
        """
        logger.info("Permission audit",
                   user_id=user_id,
                   role=user_role.value,
                   permission=permission.value,
                   granted=granted,
                   audit=True)


# Global RBAC manager instance
rbac_manager = None


def get_rbac_manager(settings=None) -> RBACManager:
    """
    Get or create RBAC manager instance.
    
    Args:
        settings: Enterprise settings instance
        
    Returns:
        RBACManager instance
    """
    global rbac_manager
    if rbac_manager is None:
        rbac_manager = RBACManager(settings)
    return rbac_manager 