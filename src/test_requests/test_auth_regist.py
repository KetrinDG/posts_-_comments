import requests
import string
import random

def string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    Generate a random string of a given size.

    Args:
    - size (int): The length of the generated string. Default is 6.
    - chars (str): The set of characters to choose from. Default is uppercase letters and digits.

    Returns:
    - str: A randomly generated string of the specified size.
    """
    return "".join(random.choice(chars) for _ in range(size))

def perform_login_test(host, headers, default_timeout):
    """
    Test the login functionality with incorrect credentials.

    Args:
    - host (str): The base URL of the application.
    - headers (dict): Headers to include in the request.
    - default_timeout (int): The timeout for the request in seconds.

    Returns:
    - bool: True if the test passes (status code 401), False otherwise.
    """
    print("########### - AUTHORIZATION NEGATIVE CASE - ##############################")
    body = {
        "email": "wrooooooooooooongpassword@test.com",
        "password": "wrooooooooooooongpassword123-Ok",
    }

    r = requests.post(
        f"{host}/login/", json=body, headers=headers, timeout=default_timeout
    )
    print("|")
    if r.status_code == 401:
        print("| TEST PASSED | time = ", r.elapsed.total_seconds(), "| response - ", r.text)
        return True
    else:
        print("| TEST FAILED - ", r.status_code)
        return False

def perform_registration_test(host, headers, default_timeout):
    """
    Test the registration functionality by attempting double registration with different emails.

    Args:
    - host (str): The base URL of the application.
    - headers (dict): Headers to include in the request.
    - default_timeout (int): The timeout for the request in seconds.

    Returns:
    - bool: True if the test passes (both registrations succeed), False otherwise.
    """
    print("########### - DOUBLE REGISTRATION NEGATIVE CASE - ########################")
    # First registration
    body1 = {
        "username": string_generator(size=8) + " " + string_generator(size=8),
        "email": string_generator(size=18).lower() + "@test.com",
        "password": string_generator(size=8) + "123AA!",
    }

    r1 = requests.post(
        f"{host}/registration/", json=body1, headers=headers, timeout=default_timeout
    )

    # Second registration with different email
    body2 = {
        "username": string_generator(size=8) + " " + string_generator(size=8),
        "email": string_generator(size=18).lower() + "@test2.com",  # Different email
        "password": string_generator(size=8) + "123BB!",
    }

    r2 = requests.post(
        f"{host}/registration/", json=body2, headers=headers, timeout=default_timeout
    )
    print("|")
    if r1.status_code == 200 and r2.status_code == 200:
        print("| TEST PASSED | time = ", r1.elapsed.total_seconds(), "| response - ", r1.text)
        return True
    else:
        print("| TEST FAILED - ", r1.status_code, r2.status_code)
        return False

def perform_invalid_email_test(host, headers, default_timeout):
    """
    Test the registration functionality with an invalid email format.

    Args:
    - host (str): The base URL of the application.
    - headers (dict): Headers to include in the request.
    - default_timeout (int): The timeout for the request in seconds.

    Returns:
    - bool: True if the test passes (status code 422), False otherwise.
    """
    print("########### - INVALID EMAIL NEGATIVE CASE - ###############################")
    body = {
        "username": string_generator(size=8) + " " + string_generator(size=8),
        "email": string_generator(size=18).lower(),
        "password": string_generator(size=8) + "OkA",
    }

    r = requests.post(
        f"{host}/registration/", json=body, headers=headers, timeout=default_timeout
    )

    print("|")
    if r.status_code == 422:
        print("| TEST PASSED | time = ", r.elapsed.total_seconds(), "| response - ", r.text)
        return True
    else:
        print("| TEST FAILED - ", r.status_code)
        return False

def perform_registration_and_login_test(host, headers, default_timeout):
    """
    Test the registration and login functionality with valid credentials.

    Args:
    - host (str): The base URL of the application.
    - headers (dict): Headers to include in the request.
    - default_timeout (int): The timeout for the request in seconds.

    Returns:
    - bool: True if the test passes (registration and login succeed), False otherwise.
    """
    print("########### - REGISTRATION + AUTHORIZATION POSITIVE CASE - ###############")
    body = {
        "username": string_generator(size=8) + " " + string_generator(size=8),
        "email": string_generator(size=18).lower() + "@test.com",
        "password": "123" + string_generator(size=4).lower() + "AAA!"
    }

    r = requests.post(
        f"{host}/registration/", json=body, headers=headers, timeout=default_timeout
    )
    print("registration - ", r.text)

    username = body["username"]
    del body["username"]

    r = requests.post(
        f"{host}/login/", json=body, headers=headers, timeout=default_timeout
    )
    print("|")
    if (
        r.status_code == 200
        and r.json()["user"]["username"] == username
        and r.json()["user"]["email"] == body["email"]
    ):
        print(
            "| TEST PASSED | time = ",
            r.elapsed.total_seconds(),
            "| response token - ",
            r.json()["access_token"],
            r.json()["user"]["id"],
        )
        return True
    else:
        print("| TEST FAILED - ", r.status_code)
        return False

def run_tests(host):
    """
    Run all defined tests and print the results.

    Args:
    - host (str): The base URL of the application.
    """
    default_timeout = 10
    headers = {"content-type": "application/json"}

    tests = [
        perform_login_test,
        perform_registration_test,
        perform_invalid_email_test,
        perform_registration_and_login_test,
    ]

    test_results = {}

    for test in tests:
        test_name = test.__name__.replace('_', ' ').title()
        test_result = test(host, headers, default_timeout)  # Pass headers here
        test_results[test_name] = "PASSED" if test_result else "FAILED"

    print("################## - TEST SUMMARY - #####################################")
    for key, value in test_results.items():
        if value == "PASSED":
            print("✅", value, " -  ", key)
        else:
            print("📛", value, " -  ", key)

    print("##########################################################################")

if __name__ == "__main__":
    host = "http://127.0.0.1:8000"  # or your actual host IP
    run_tests(host)
