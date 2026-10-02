from app.services.auth.security import (
    hash_password,
    verify_password,
)


password = "StrongPassword123"

hashed_password = hash_password(password)

print("\n========== PASSWORD HASH ==========")
print(hashed_password)

print("\n========== VERIFY CORRECT PASSWORD ==========")
print(verify_password(
    password,
    hashed_password,
))

print("\n========== VERIFY WRONG PASSWORD ==========")
print(verify_password(
    "WrongPassword",
    hashed_password,
))