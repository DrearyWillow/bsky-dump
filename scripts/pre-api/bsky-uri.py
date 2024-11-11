def post_url_to_at_uri(post_url):
    # Split the URL to extract handle (or DID) and post ID (RKEY)
    parts = post_url.rstrip('/').split('/')
    
    # Handle/authority is the username or DID part
    authority = parts[-3]  # "username" in the example URL
    
    # Record key (RKEY) is the post ID
    rkey = parts[-1]  # "3xyz45abc" in the example
    
    # Collection for Bluesky posts is typically 'app.bsky.feed.post'
    collection = 'app.bsky.feed.post'
    
    # Construct and return the AT URI
    at_uri = f"at://{authority}/{collection}/{rkey}"
    return at_uri

# Example usage
post_url = "https://bsky.app/profile/bsky.mom/post/3l47gcq5f7627"
at_uri = post_url_to_at_uri(post_url)
print(f"AT URI: {at_uri}")

