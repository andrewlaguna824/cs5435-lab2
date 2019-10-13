from bottle import (
    post,
    request,
    response,
    jinja2_template as template,
)

from app.models.user import (
    get_user,
)

from app.models.session import (
    logged_in,
)


@post('/pay')
@logged_in
def do_payment(db, session):
    sender = get_user(db, session.get_username())

    # Check validity of anti csrf token before sending payment
    # CSRF token from form
    csrf_token = request.forms.get("anticsrf_token")
    print("csrf token from form: {}".format(csrf_token))

    # Session cookie
    cookie = request.get_cookie("session")
    print(request.get_cookie("session"))

    # Compare values
    if csrf_token != cookie:
        response.status = 400
        error = "Potential CSRF Attack"
        print("CSRF Attack")
        return template(
            "profile",
            user=sender,
            session_user=sender,
            payment_error=error,
        )

    recipient = db.execute(
        "SELECT * FROM users WHERE users.username='{}' LIMIT 1 OFFSET 0".format(
            request.forms.get('recipient')
        )
    ).fetchone()
    payment_amount = int(request.forms.get('amount'))
    error = None
    if (sender.get_coins() < payment_amount):
        response.status = 400
        error = "Not enough funds."
    elif (payment_amount < 0):
        response.status = 400
        error = "Payment amount cannot be negative."
    elif (recipient is None):
        response.status = 400
        error = "Recipient {} does not exist.".format(request.forms.get('recipient'))
    elif (recipient['username'] == sender.username):
        response.status = 400
        error = "Cannot pay self."
    else:
        sender.debit_coins(payment_amount)
        db.execute(
            "UPDATE users SET coins={} WHERE users.username='{}'".format(
                recipient['coins'] + payment_amount, recipient['username']
            )
        )
    return template(
        "profile",
        user=sender,
        session_user=sender,
        payment_error=error,
    )

