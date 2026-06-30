import requests

def test():
    session = requests.Session()
    # First GET to check cookies/redirects
    r_get = session.get('https://c69.us/dashboard/login/')
    print("GET status:", r_get.status_code)
    print("GET cookies:", session.cookies.get_dict())
    
    # POST login
    headers = {'X-CSRFToken': session.cookies.get('csrftoken', '')}
    r_post = session.post('https://c69.us/dashboard/login/', json={'username': 'testuser', 'password': 'wrongpassword'}, headers=headers)
    print("POST status:", r_post.status_code)
    print("POST text:", r_post.text)

if __name__ == '__main__':
    test()
