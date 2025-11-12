"""
Role-Based Access Control System for Dumroo AI Admin Panel
Handles user authentication, authorization, and data access permissions
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum
import json
import hashlib

class AccessLevel(Enum):
    SUPER_ADMIN = "super_admin"      # Full access to all data
    REGION_ADMIN = "region_admin"    # Access to specific region data
    GRADE_ADMIN = "grade_admin"      # Access to specific grade data
    CLASS_ADMIN = "class_admin"      # Access to specific class data
    SUBJECT_ADMIN = "subject_admin"  # Access to specific subject data

@dataclass
class UserPermissions:
    """Defines what data a user can access"""
    access_level: AccessLevel
    regions: List[str] = None
    grades: List[str] = None
    classes: List[str] = None
    subjects: List[str] = None
    can_view_sensitive_data: bool = False
    can_export_data: bool = False

@dataclass
class AdminUser:
    """Represents an admin user with their permissions"""
    username: str
    password_hash: str
    full_name: str
    email: str
    permissions: UserPermissions
    is_active: bool = True
    created_date: str = None

class RoleBasedAccessControl:
    """Main RBAC system for managing user permissions and data access"""
    
    def __init__(self):
        self.users: Dict[str, AdminUser] = {}
        self.active_sessions: Dict[str, str] = {}  # session_id -> username
        self._initialize_default_users()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _initialize_default_users(self):
        """Create default admin users with different permission levels"""
        
        # Super Admin - Full access
        super_admin = AdminUser(
            username="super_admin",
            password_hash=self._hash_password("admin123"),
            full_name="Super Administrator",
            email="super@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.SUPER_ADMIN,
                can_view_sensitive_data=True,
                can_export_data=True
            ),
            created_date="2025-11-12"
        )
        
        # North Region Admin
        north_admin = AdminUser(
            username="north_admin",
            password_hash=self._hash_password("north123"),
            full_name="North Region Administrator",
            email="north@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.REGION_ADMIN,
                regions=["North"],
                can_view_sensitive_data=True,
                can_export_data=True
            ),
            created_date="2025-11-12"
        )
        
        # South Region Admin
        south_admin = AdminUser(
            username="south_admin",
            password_hash=self._hash_password("south123"),
            full_name="South Region Administrator",
            email="south@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.REGION_ADMIN,
                regions=["South"],
                can_view_sensitive_data=True,
                can_export_data=False
            ),
            created_date="2025-11-12"
        )
        
        # Grade 8 & 9 Admin
        grade_admin = AdminUser(
            username="grade89_admin",
            password_hash=self._hash_password("grade123"),
            full_name="Grade 8-9 Administrator",
            email="grade89@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.GRADE_ADMIN,
                grades=["Grade 8", "Grade 9"],
                can_view_sensitive_data=False,
                can_export_data=False
            ),
            created_date="2025-11-12"
        )
        
        # Class A & B Admin (All Grades)
        class_admin = AdminUser(
            username="classab_admin",
            password_hash=self._hash_password("class123"),
            full_name="Class A-B Administrator",
            email="classab@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.CLASS_ADMIN,
                classes=["A", "B"],
                can_view_sensitive_data=False,
                can_export_data=False
            ),
            created_date="2025-11-12"
        )
        
        # Math & Science Subject Admin
        subject_admin = AdminUser(
            username="mathsci_admin",
            password_hash=self._hash_password("subject123"),
            full_name="Math & Science Administrator",
            email="mathsci@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.SUBJECT_ADMIN,
                subjects=["Mathematics", "Science"],
                can_view_sensitive_data=False,
                can_export_data=False
            ),
            created_date="2025-11-12"
        )
        
        # East Region + Grade 6-7 Admin (Combined permissions)
        combined_admin = AdminUser(
            username="east67_admin",
            password_hash=self._hash_password("combined123"),
            full_name="East Region Grade 6-7 Administrator",
            email="east67@dumroo.ai",
            permissions=UserPermissions(
                access_level=AccessLevel.REGION_ADMIN,
                regions=["East"],
                grades=["Grade 6", "Grade 7"],
                can_view_sensitive_data=False,
                can_export_data=True
            ),
            created_date="2025-11-12"
        )
        
        # Add all users to the system
        users = [super_admin, north_admin, south_admin, grade_admin, 
                class_admin, subject_admin, combined_admin]
        
        for user in users:
            self.users[user.username] = user
    
    def authenticate_user(self, username: str, password: str) -> Optional[AdminUser]:
        """Authenticate user login"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if not user.is_active:
            return None
        
        password_hash = self._hash_password(password)
        if user.password_hash == password_hash:
            return user
        
        return None
    
    def get_user_permissions(self, username: str) -> Optional[UserPermissions]:
        """Get permissions for a specific user"""
        if username in self.users:
            return self.users[username].permissions
        return None
    
    def can_access_data(self, username: str, data_filters: Dict) -> bool:
        """Check if user can access data based on filters"""
        permissions = self.get_user_permissions(username)
        if not permissions:
            return False
        
        # Super admin can access everything
        if permissions.access_level == AccessLevel.SUPER_ADMIN:
            return True
        
        # Check region access
        if permissions.regions and 'region' in data_filters:
            if data_filters['region'] not in permissions.regions:
                return False
        
        # Check grade access
        if permissions.grades and 'grade' in data_filters:
            if data_filters['grade'] not in permissions.grades:
                return False
        
        # Check class access
        if permissions.classes and 'class_section' in data_filters:
            if data_filters['class_section'] not in permissions.classes:
                return False
        
        # Check subject access
        if permissions.subjects and 'subject' in data_filters:
            if data_filters['subject'] not in permissions.subjects:
                return False
        
        return True
    
    def get_allowed_filters(self, username: str) -> Dict:
        """Get the allowed data filters for a user"""
        permissions = self.get_user_permissions(username)
        if not permissions:
            return {}
        
        # Super admin has no restrictions
        if permissions.access_level == AccessLevel.SUPER_ADMIN:
            return {}
        
        filters = {}
        
        if permissions.regions:
            filters['region'] = permissions.regions
        if permissions.grades:
            filters['grade'] = permissions.grades
        if permissions.classes:
            filters['class_section'] = permissions.classes
        if permissions.subjects:
            filters['subject'] = permissions.subjects
        
        return filters
    
    def get_all_users(self) -> List[Dict]:
        """Get information about all users (for admin panel)"""
        users_info = []
        for username, user in self.users.items():
            user_info = {
                "username": username,
                "full_name": user.full_name,
                "email": user.email,
                "access_level": user.permissions.access_level.value,
                "is_active": user.is_active,
                "restrictions": {
                    "regions": user.permissions.regions,
                    "grades": user.permissions.grades,
                    "classes": user.permissions.classes,
                    "subjects": user.permissions.subjects
                },
                "capabilities": {
                    "can_view_sensitive_data": user.permissions.can_view_sensitive_data,
                    "can_export_data": user.permissions.can_export_data
                }
            }
            users_info.append(user_info)
        
        return users_info
    
    def save_users_to_file(self, filename: str = "config/users.json"):
        """Save user configuration to JSON file"""
        users_data = {}
        for username, user in self.users.items():
            users_data[username] = {
                "username": user.username,
                "password_hash": user.password_hash,
                "full_name": user.full_name,
                "email": user.email,
                "is_active": user.is_active,
                "created_date": user.created_date,
                "permissions": {
                    "access_level": user.permissions.access_level.value,
                    "regions": user.permissions.regions,
                    "grades": user.permissions.grades,
                    "classes": user.permissions.classes,
                    "subjects": user.permissions.subjects,
                    "can_view_sensitive_data": user.permissions.can_view_sensitive_data,
                    "can_export_data": user.permissions.can_export_data
                }
            }
        
        with open(filename, 'w') as f:
            json.dump(users_data, f, indent=2)

# Initialize RBAC system
rbac = RoleBasedAccessControl()

if __name__ == "__main__":
    # Save user configuration to file
    rbac.save_users_to_file()
    
    # Display all users and their permissions
    print("=== DUMROO AI ADMIN PANEL - USER ACCOUNTS ===\n")
    
    users = rbac.get_all_users()
    for user in users:
        print(f"Username: {user['username']}")
        print(f"Full Name: {user['full_name']}")
        print(f"Email: {user['email']}")
        print(f"Access Level: {user['access_level']}")
        print(f"Active: {user['is_active']}")
        
        restrictions = user['restrictions']
        if any(restrictions.values()):
            print("Restrictions:")
            if restrictions['regions']:
                print(f"  - Regions: {', '.join(restrictions['regions'])}")
            if restrictions['grades']:
                print(f"  - Grades: {', '.join(restrictions['grades'])}")
            if restrictions['classes']:
                print(f"  - Classes: {', '.join(restrictions['classes'])}")
            if restrictions['subjects']:
                print(f"  - Subjects: {', '.join(restrictions['subjects'])}")
        else:
            print("Restrictions: None (Full Access)")
        
        capabilities = user['capabilities']
        print(f"Can view sensitive data: {capabilities['can_view_sensitive_data']}")
        print(f"Can export data: {capabilities['can_export_data']}")
        print("-" * 50)
    
    # Test authentication
    print("\n=== TESTING AUTHENTICATION ===")
    test_users = [
        ("super_admin", "admin123"),
        ("north_admin", "north123"),
        ("grade89_admin", "grade123"),
        ("invalid_user", "wrong_password")
    ]
    
    for username, password in test_users:
        user = rbac.authenticate_user(username, password)
        if user:
            print(f"✓ {username}: Authentication successful")
        else:
            print(f"✗ {username}: Authentication failed")