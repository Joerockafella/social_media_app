import uuid #Universal Unique Identifier

# The slug field will help generate a user name from first and last name
# This is to help generate random code to add on a username when users have similar names

def get_random_code():
    code = str(uuid.uuid4())[:8].replace('-', '').lower()
    return code 