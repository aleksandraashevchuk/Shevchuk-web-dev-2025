def test_get_by_id_with_existing_user(user_repository, existing_user):
    user = user_repository.get_by_id(existing_user.id)
    assert user is not None
    assert user.id == existing_user.id
    assert user.username == existing_user.username

def test_get_by_id_with_nonexisting_user(user_repository, nonexisting_user_id):
    user = user_repository.get_by_id(nonexisting_user_id)
    assert user is None

def test_get_by_username_and_password(user_repository, existing_user):
    user = user_repository.get_by_username_and_password(existing_user.username, existing_user.password_hash)
    assert user is not None
    assert user.username == existing_user.username

def test_get_all_with_users(user_repository, existing_user):
    users = user_repository.get_all()
    assert any(u.id == existing_user.id for u in users)

def test_check_password(user_repository, existing_user):
    assert user_repository.check_password(existing_user.id, existing_user.password_hash) is True
    assert user_repository.check_password(existing_user.id, "wrongpassword") is False

def test_update_password(user_repository, existing_user):
    new_password = "newpass123"
    user_repository.update_password(existing_user.id, new_password)
    assert user_repository.check_password(existing_user.id, new_password)

def test_create_and_delete_user(created_user, user_repository):
    user = user_repository.get_by_id(created_user.id)
    assert user is not None

    user_repository.delete(created_user.id)
    assert user_repository.get_by_id(created_user.id) is None

def test_update_user(updated_user, user_repository):
    user = user_repository.get_by_id(updated_user.id)
    assert user.first_name == "Updated"
    assert user.middle_name == "X"
    assert user.last_name == "Y"