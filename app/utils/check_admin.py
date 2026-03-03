import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.database import info_user, ADMIN_USERNAME, ADMIN_EMAIL

def check_admin():
    print(f"Checking for admin user: {ADMIN_USERNAME}")
    print(f"Admin email: {ADMIN_EMAIL}")
    print("-" * 50)
    
    user = info_user(ADMIN_USERNAME)
    if user:
        print(f"Admin found in database!")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        if user['email'] == ADMIN_EMAIL:
            print("Email matches")
        else:
            print(f"Email mismatch! DB: {user['email']}")
    else:
        print(f"Admin not found in database!")
        print(f"Please register with username '{ADMIN_USERNAME}'")
        print(f"or email '{ADMIN_EMAIL}'")

if __name__ == "__main__":
    check_admin()