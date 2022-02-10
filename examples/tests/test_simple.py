
def test_getting_posts_all(users_route):
    c = {
        "name":"Tenali Ramakrishna",
        "gender":"male",
        "email":"tenali.ramakrishna@15ce.com",
        "status":"active"
    }
    response = users_route.append_header('Authorization', 'Bearer ACCESS-TOKEN').get(data=c)
    print(response)
