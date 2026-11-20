# Workforce Service API endpoint purposes

The endpoints use the `/api/v1/workforce` base path. Examples assume the
service is running locally on port `5000`. Replace the token and sample values
with valid ones for your environment. Protected endpoints require a bearer
access token.

* `/api/v1/workforce/health` [GET]:
    * Check whether the Workforce Service can reach its database.
    * Return the service and database connectivity status.

  ```bash
  curl -i http://127.0.0.1:5000/api/v1/workforce/health
  ```

* `/api/v1/workforce/users` [POST]:
    * Create a user account. Admin access is required.
    * Validate the submitted profile and role, hash the password, and save the user.
    * Return the safe user profile without the password or password hash.

  ```bash
  curl -i -X POST http://127.0.0.1:5000/api/v1/workforce/users \
    -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"email":"tech@example.com","display_name":"Taylor Technician","password":"ReplaceWithASecret","role":"Technician","is_active":true}'
  ```

* `/api/v1/workforce/login` [POST]:
    * Accept an email and password as JSON and validate the input.
    * Find the account and compare the password with its stored password hash.
    * Reject unknown or inactive accounts and incorrect passwords.
    * On success, return a short-lived access token containing the user ID and role.

  ```bash
  curl -i -X POST http://127.0.0.1:5000/api/v1/workforce/login \
    -H "Content-Type: application/json" \
    -d '{"email":"tech@example.com","password":"ReplaceWithASecret"}'
  ```

* `/api/v1/workforce/me` [GET]:
    * Verify the bearer token and identify the signed-in user from its subject claim.
    * Return the current user's safe profile (ID, email, display name, and role).
    * Reject invalid tokens or unavailable/inactive accounts.

  ```bash
  curl -i http://127.0.0.1:5000/api/v1/workforce/me \
    -H "Authorization: Bearer USER_ACCESS_TOKEN"
  ```

* `/api/v1/workforce/users` [GET]:
    * List user profiles. Admin or Manager access is required.
    * Optionally filter by `role`, `name_or_email_pattern`, and `is_active`.
    * Support `limit` and `offset` for paginated results.
    * Return safe profile fields only; never return passwords or password hashes.

  ```bash
  curl -i -G http://127.0.0.1:5000/api/v1/workforce/users \
    -H "Authorization: Bearer ADMIN_OR_MANAGER_ACCESS_TOKEN" \
    --data-urlencode "role=Technician" \
    --data-urlencode "name_or_email_pattern=taylor" \
    --data-urlencode "is_active=true" \
    --data-urlencode "limit=20" \
    --data-urlencode "offset=0"
  ```

* `/api/v1/workforce/users/{user_id}` [GET]:
    * Retrieve one user's safe profile by UUID. Admin or Manager access is required.
    * Return `404` when the requested user does not exist.

  ```bash
  curl -i http://127.0.0.1:5000/api/v1/workforce/users/USER_UUID \
    -H "Authorization: Bearer ADMIN_OR_MANAGER_ACCESS_TOKEN"
  ```

* `/api/v1/workforce/users/{user_id}` [PATCH]:
    * Partially update an existing user's permitted profile fields. Admin access is required.
    * Accept only fields included in the request, such as email, display name, role,
      or active status.
    * Return the updated safe profile; reject invalid fields or values.

  ```bash
  curl -i -X PATCH http://127.0.0.1:5000/api/v1/workforce/users/USER_UUID \
    -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"display_name":"Taylor A. Technician","is_active":true}'
  ```
