def test_user_password_hashing_behaves_correctly(current_user):
    password = "abc123"

    current_user.set_password(password)

    assert current_user.password_hash
    assert current_user.password_hash != password
    assert current_user.check_password(password)


def test_user_rejects_wrong_password(current_user):
    current_user.set_password("abc123")

    assert not current_user.check_password("cde456")
