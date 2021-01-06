from api.src import utils, database, schemas


def test_should_return_triggers(session):
    triggers = session.query(database.Trigger).all()
    assert len(triggers) == 4


def test_get_user_triggers_returns_triggers(session, users, triggers):
    triggers = utils.get_user_triggers(users[0].id, session)
    correct_triggers = [t for t in triggers if t.user_id == users[0].id]
    assert len(triggers) == len(correct_triggers)
    assert isinstance(triggers[0], schemas.Trigger)


def test_clean_unused_triggers_should_delete_from_db(session, users):
    old_triggers = utils.get_user_triggers(users[0].id, session)
    utils.clean_unused_triggers(users[0], old_triggers, [], session)
    new_triggers = utils.get_user_triggers(users[0].id, session)
    assert len(old_triggers) != len(new_triggers)


def test_get_users_returns_users(session, users):
    db_users = utils.get_users(session)
    assert len(db_users) == len(users)


def test_get_user_trigger_alerts_returns_alerts(session):
    alerts = utils.get_user_trigger_alerts(0, 0, session)
    for alert in alerts:
        assert alert.user_id == 0
        assert alert.trigger_id == 0


def test_get_user_by_username_returns_users(session, users):
    username = users[0].username
    user = utils.get_user_by_username(username, session)
    assert user.username == username
