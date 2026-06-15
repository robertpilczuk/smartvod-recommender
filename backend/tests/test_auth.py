import auth


def test_hash_is_not_plaintext_and_verifies():
    h = auth.hash_password("123")
    assert h != "123"
    assert auth.verify_password("123", h)
    assert not auth.verify_password("inne", h)


def test_simple_passwords_allowed():
    # Demo dopuszcza krótkie hasła
    for pwd in ["1", "abc", "0000"]:
        assert auth.verify_password(pwd, auth.hash_password(pwd))
