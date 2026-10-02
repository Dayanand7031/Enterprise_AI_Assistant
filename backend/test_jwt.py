from app.services.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


user_id = 1


access_token = create_access_token(user_id)

refresh_token = create_refresh_token(user_id)


print("\n========== ACCESS TOKEN ==========")
print(access_token)

print("\n========== ACCESS TOKEN PAYLOAD ==========")
print(decode_token(access_token))


print("\n========== REFRESH TOKEN ==========")
print(refresh_token)

print("\n========== REFRESH TOKEN PAYLOAD ==========")
print(decode_token(refresh_token))