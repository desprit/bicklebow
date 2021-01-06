import sys
from typing import Optional

from api.src import utils, tinkoff, database


def main(user_id: Optional[int] = None) -> None:
    """
    Check user triggers and send alerts if needed.
    """
    with database.get_db_session() as session:
        users = utils.get_users(session)
        if user_id is not None:
            users = [u for u in users if u.id == user_id]
        for user in users:
            triggers = utils.get_user_triggers(user.id, session)
            positions = tinkoff.get_user_positions(user)
            utils.clean_unused_triggers(user, triggers, positions, session)
            portfolio_tickers = [p.ticker for p in positions]
            triggers = [
                t for t in triggers if (not t.ticker or t.ticker in portfolio_tickers)
            ]
            for position in positions:
                for t in triggers:
                    if t.is_triggered(position) and not utils.should_ignore(t):
                        utils.send_alert(user, t, position)
                        utils.save_alert(user, t, session)


if __name__ == "__main__":
    user_id = None
    if len(sys.argv) == 2:
        user_id = int(sys.argv[1])
    main(user_id)
