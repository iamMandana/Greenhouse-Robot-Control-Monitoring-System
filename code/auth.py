import json
import hashlib
import os
import pyotp
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
import random

FILE = "users.json"

class AuthSystem:
    def __init__(self):
        self.users = {}
        self.attempts = {}
        self.temp_reset_codes = {}
        self.load_users()

    def hash_password(self, password):
        if password is None:
            return ""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        if not os.path.exists(FILE):
            self.users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "locked": False,
                    "locked_by_admin": False,  # Track if admin locked the account
                    "totp_secret": None,
                    "totp_enabled": False
                }
            }
            self.save_users()
        else:
            with open(FILE, "r") as f:
                self.users = json.load(f)

    def save_users(self):
        with open(FILE, "w") as f:
            json.dump(self.users, f, indent=4)

    def setup_2fa(self, username):
        """Generate TOTP secret and QR code for first-time setup"""
        if username not in self.users:
            return None, None, "User not found"
        
        secret = pyotp.random_base32()
        self.users[username]["totp_secret"] = secret
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=username, 
            issuer_name="Greenhouse Robot System"
        )
        
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        self.save_users()
        return secret, img_base64, "Success"
    
    def verify_2fa_enrollment(self, username, totp_code):
        """Verify TOTP code during enrollment"""
        if username not in self.users:
            return False, "User not found"
        
        secret = self.users[username].get("totp_secret")
        if not secret:
            return False, "2FA not set up for this user"
        
        totp = pyotp.TOTP(secret)
        if totp.verify(totp_code):
            self.users[username]["totp_enabled"] = True
            self.save_users()
            return True, "2FA enabled successfully"
        
        return False, "Invalid verification code"

    def login(self, username, password, totp_code=None):
        if username not in self.users:
            return False, "User not found"

        user = self.users[username]

        # Check if account is locked
        if user.get("locked", False):
            # Check if locked by admin
            if user.get("locked_by_admin", False):
                return False, "Account locked by administrator. Please contact admin."
            else:
                return False, "Account is locked. Use 'Unlock Account' option with your authenticator app."

        # Handle password check
        if password is not None:
            if self.hash_password(password) != user["password"]:
                self.attempts[username] = self.attempts.get(username, 0) + 1
                
                if self.attempts[username] >= 3:
                    user["locked"] = True
                    user["locked_by_admin"] = False  # Locked due to failed attempts
                    self.save_users()
                    return False, "Account locked due to multiple failed attempts"
                
                remaining = 3 - self.attempts[username]
                return False, f"Wrong password. {remaining} attempts remaining"

        # Check 2FA if enabled
        if user.get("totp_enabled", False):
            if not totp_code:
                return False, "2FA_REQUIRED"
            
            secret = user.get("totp_secret")
            if not secret:
                return False, "2FA configuration error"
            
            totp = pyotp.TOTP(secret)
            if not totp.verify(totp_code):
                self.attempts[username] = self.attempts.get(username, 0) + 1
                if self.attempts[username] >= 3:
                    if user["role"] != "admin":
                        user["locked"] = True
                        user["locked_by_admin"] = False
                        self.save_users()
                        return False, "Account locked due to multiple 2FA failures"
                return False, "Invalid 2FA code"
        
        self.attempts[username] = 0
        return True, user["role"]

    def unlock_account(self, username, totp_code):
        """Unlock locked account using 2FA (only for non-admin locks)"""
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        # Check if locked by admin
        if user.get("locked_by_admin", False):
            return False, "Account was locked by administrator. Please contact admin to unlock."
        
        if not user.get("locked", False):
            return False, "Account is not locked"
        
        if not user.get("totp_enabled", False):
            return False, "2FA not enabled for this account. Contact admin."
        
        secret = user.get("totp_secret")
        if not secret:
            return False, "2FA configuration error"
        
        totp = pyotp.TOTP(secret)
        if totp.verify(totp_code):
            user["locked"] = False
            user["locked_by_admin"] = False
            self.attempts[username] = 0
            self.save_users()
            return True, "Account unlocked successfully"
        
        return False, "Invalid 2FA code"

    def request_password_reset(self, username):
        """Request password reset - user must provide 2FA code"""
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        # Check if locked by admin
        if user.get("locked_by_admin", False):
            return False, "Account locked by administrator. Please contact admin."
        
        if not user.get("totp_enabled", False):
            return False, "2FA not enabled. Contact admin for password reset."
        
        return True, "2FA_REQUIRED_FOR_RESET"
    
    def reset_password_with_2fa(self, username, totp_code, new_password):
        """Reset password using 2FA code from authenticator app"""
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        
        # Check if locked by admin
        if user.get("locked_by_admin", False):
            return False, "Account locked by administrator. Please contact admin."
        
        if not user.get("totp_enabled", False):
            return False, "2FA not enabled for this account"
        
        secret = user.get("totp_secret")
        if not secret:
            return False, "2FA configuration error"
        
        totp = pyotp.TOTP(secret)
        if totp.verify(totp_code):
            self.users[username]["password"] = self.hash_password(new_password)
            self.users[username]["locked"] = False
            self.users[username]["locked_by_admin"] = False
            self.attempts[username] = 0
            self.save_users()
            return True, "Password reset successfully"
        
        return False, "Invalid 2FA code"

    def add_user(self, username, password, role):
        if username in self.users:
            return False

        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "locked": False,
            "locked_by_admin": False,
            "totp_secret": None,
            "totp_enabled": False
        }
        self.save_users()
        return True

    def delete_user(self, username):
        if username == "admin":
            return False
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True
        return False

    def unlock_user(self, username):
        """Admin unlock user - can unlock any account"""
        if username in self.users:
            self.users[username]["locked"] = False
            self.users[username]["locked_by_admin"] = False
            self.save_users()
            return True
        return False

    def change_password(self, username, old_pw, new_pw):
        if username in self.users:
            if self.hash_password(old_pw) == self.users[username]["password"]:
                self.users[username]["password"] = self.hash_password(new_pw)
                self.save_users()
                return True
        return False

    def admin_reset_password(self, username):
        if username in self.users:
            self.users[username]["password"] = self.hash_password("1234")
            self.users[username]["locked"] = False
            self.users[username]["locked_by_admin"] = False
            self.save_users()
            return True
        return False

    def get_all_users(self):
        return self.users
    
    def lock_user(self, username):
        """Admin lock user - cannot be unlocked by user"""
        if username in self.users:
            self.users[username]["locked"] = True
            self.users[username]["locked_by_admin"] = True  # Mark as admin lock
            self.save_users()
            return True
        return False
    
    def is_2fa_enabled(self, username):
        """Check if user has 2FA enabled"""
        if username in self.users:
            return self.users[username].get("totp_enabled", False)
        return False
    
    def disable_2fa(self, username):
        """Disable 2FA for user"""
        if username in self.users:
            self.users[username]["totp_enabled"] = False
            self.users[username]["totp_secret"] = None
            self.save_users()
            return True
        return False
