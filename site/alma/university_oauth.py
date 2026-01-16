
# User info handling

def account_info(remote, resp):
    
    """Extract user information from Dex response."""
    return {
        'user': {
            'email': resp.get('email'),
            'profile': {
                'username': resp.get('sAMAccountName', resp['email'].split('@')[0]),
                'full_name': resp.get('displayName'),
            }
        },
        'external_id': resp['sub'],
        'external_method': 'dex',
    }

def account_setup(remote, token, resp):
    """Perform post-login account setup (e.g., link roles/groups)."""
    # Add custom logic here if needed
    pass
