import os
from supabase import create_client, Client

supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client for user-facing operations
supabase: Client = create_client(supabase_url, supabase_anon_key)

# Client for admin operations (service role)
supabase_admin: Client = create_client(supabase_url, supabase_service_role_key)


async def get_user_from_token(token: str) -> dict:
    """Get user info from JWT token"""
    try:
        user = supabase.auth.get_user(token)
        return user
    except Exception as e:
        return None


async def get_or_create_user(email: str) -> dict:
    """Get or create user by email"""
    try:
        # Check if user exists
        response = supabase.table("users").select("*").eq("email", email).execute()

        if response.data:
            return response.data[0]
        else:
            # Create new user
            new_user = {"email": email, "subscription_tier": "free"}
            response = supabase.table("users").insert(new_user).execute()
            return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting/creating user: {e}")
        return None
