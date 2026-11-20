# Deep dive to the API endpoint's purposes

What each endpoint does is documented in the following format:
* endpoint_path:  
    list of tasks it's responsible for...  


* /api/v1/workforce/login:
    * Accept an email and password as JSON and validate the input.  
    * Fetch and compare user and their password to the stored password hash.
    * Reject unknown or inactive user requests with a generic message.
    * On success, return a short-lived token containing the user ID and role.

* /api/v1/workforce/
    