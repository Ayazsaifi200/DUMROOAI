#!/usr/bin/env python3
"""
Secret Key Generator for Dumroo AI Project
"""
import secrets
import string
import random

def generate_secret_key(length=64):
    """Generate a secure secret key"""
    return secrets.token_urlsafe(length)

def generate_custom_secret():
    """Generate a custom secret with mixed characters"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(64))

if __name__ == "__main__":
    print("🔐 SECRET KEY GENERATOR FOR DUMROO AI")
    print("=" * 50)
    
    # Method 1: URL-safe base64
    key1 = generate_secret_key()
    print(f"Method 1 (Recommended):\nSECRET_KEY={key1}\n")
    
    # Method 2: Custom mixed characters
    key2 = generate_custom_secret()
    print(f"Method 2 (Alternative):\nSECRET_KEY={key2}\n")
    
    # Method 3: Simple UUID-based
    import uuid
    key3 = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')
    print(f"Method 3 (Simple):\nSECRET_KEY={key3}\n")
    
    print("✅ Copy any one key and paste in your .env file!")
    print("💡 Recommendation: Use Method 1 for best security")