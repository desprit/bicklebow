"""
Commands available for the bot.
"""
import sys

from sqlalchemy.orm.session import Session
from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from api.src.config import settings
from api.src.keyboards import MARKUPS
from api.src import database, schemas, tinkoff, utils


(
    USER_CREATION,
    CHOOSING,
    POSITIONS,
    TRIGGERS,
    TRIGGER_CREATION,
    TRIGGER_DELETION,
    ALERTS,
) = range(7)


def format_trigger(idx: int, trigger: schemas.Trigger) -> str:
    """
    Convert database Trigger model into Telegram message.
    """
    ticker = trigger.ticker or "All markets"
    direction = trigger.direction.value.lower()
    reference = trigger.reference.value.lower()
    if "candle" in reference and "1d" in reference:
        reference = "daily candle"
    if "candle" in reference and "1w" in reference:
        reference = "weekly candle"
    if "candle" in reference and "1m" in reference:
        reference = "monthly candle"
    return f"{idx+1}. {ticker} - {direction} > {trigger.threshold}% from {reference}\n"


def format_position(idx: int, position: schemas.PortfolioPosition) -> str:
    """
    Convert PortfolioPosition into Telegram message.
    """
    prefix = "" if position.current_price > position.portfolio_price else "-"
    delta = abs(round((1 - position.current_price / position.portfolio_price) * 100, 2))
    return f"{idx+1}. {position.ticker} <b>{prefix}{delta}%</b>\n"


def format_alert(idx: int, alert: schemas.Alert, session: Session) -> str:
    """
    Convert database Alert model into Telegram message.
    """
    created_at = alert.created_at.strftime("%b'%d %H:%M:%S")
    trigger_str = "Trigger no longer present in the database"
    trigger: database.Trigger = (
        session.query(database.Trigger)
        .filter(database.Trigger.id == alert.trigger_id)
        .first()
    )
    if trigger:
        ticker = "All markets" if trigger.ticker is None else trigger.ticker
        trigger_str = f"{ticker} {trigger.direction.lower()} > {trigger.threshold}%"
    return f"{idx+1}. {created_at} - {trigger_str}\n"


def start(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    with database.get_db_session() as session:
        user = utils.get_user_by_username(username, session)
        if not user:
            update.message.reply_text(
                "I don't know you, wanna sign up?",
                reply_markup=MARKUPS["yes_no"],
            )
            return USER_CREATION
        context.user_data["user_id"] = user.id
        update.message.reply_text(
            f"Yo, {username}!",
            reply_markup=MARKUPS["start"],
        )
        return CHOOSING


def request_token(update: Update, context: CallbackContext) -> int:
    """
    Get TinkoffAPI token from user.
    """
    update.message.reply_text(
        "Send me your TinkoffAPI token",
        reply_markup=MARKUPS["empty"],
    )
    return USER_CREATION


def create_user(update: Update, context: CallbackContext) -> int:
    """
    Create new user.
    """
    token = update.message.text
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    with database.get_db_session() as session:
        user = {"token": token, "chat_id": chat_id, "username": username}
        user_model = database.User(**user)
        session.add(user_model)
        session.flush()
        session.refresh(user_model)
        context.user_data["user_id"] = user_model.id
        update.message.reply_text(
            f"Nice to meet you, {username}",
            reply_markup=MARKUPS["start"],
        )
    return CHOOSING


def status(update: Update, context: CallbackContext) -> int:
    """
    Return availability of the bot and time of the last update.
    """
    update.message.reply_text(
        "I'm ok :)",
        reply_markup=MARKUPS["start"],
    )
    return CHOOSING


def get_positions(update: Update, context: CallbackContext) -> int:
    """
    Return positions for the user.
    """
    with database.get_db_session() as session:
        username = update.message.from_user.username
        user = utils.get_user_by_username(username, session)
        positions = tinkoff.get_user_positions(user)
        message = ""
        for i, position in enumerate(positions):
            message += format_position(i, position)
        update.message.reply_text(
            f"Here is a list of your positions:\n{message}",
            reply_markup=MARKUPS["start"],
            parse_mode=ParseMode.HTML,
        )
        return CHOOSING


def get_triggers(update: Update, context: CallbackContext) -> int:
    """
    Return triggers for the user.
    """
    with database.get_db_session() as session:
        username = update.message.from_user.username
        user = utils.get_user_by_username(username, session)
        triggers = utils.get_user_triggers(user.id, session)
        if triggers:
            message = ""
            for i, trigger in enumerate(triggers):
                message += format_trigger(i, trigger)
            update.message.reply_text(
                f"Here is a list of your triggers:\n{message}",
                reply_markup=MARKUPS["triggers"],
            )
        else:
            update.message.reply_text(
                "You don't have triggers",
                reply_markup=MARKUPS["no_triggers"],
            )
        return TRIGGERS


def create_trigger(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Should it trigger on Increase or Decrease?",
        reply_markup=MARKUPS["direction"],
    )
    return TRIGGER_CREATION


def process_direction(update: Update, context: CallbackContext) -> int:
    text = update.message.text.upper()
    context.user_data["direction"] = text
    update.message.reply_text(
        "What should be the reference?",
        reply_markup=MARKUPS["reference"],
    )
    return TRIGGER_CREATION


def process_portfolio_reference(update: Update, context: CallbackContext) -> int:
    text = update.message.text.upper()
    context.user_data["reference"] = text
    update.message.reply_text(
        "Threshold in %, example:\n>>> 8",
        reply_markup=MARKUPS["only_home"],
    )
    return TRIGGER_CREATION


def process_candle_reference(update: Update, context: CallbackContext) -> int:
    text = update.message.text.upper()
    context.user_data["reference"] = text
    update.message.reply_text(
        "What is the candle type?",
        reply_markup=MARKUPS["candle"],
    )
    return TRIGGER_CREATION


def process_candle_type(update: Update, context: CallbackContext) -> int:
    text = update.message.text.upper()
    if text == "DAILY":
        context.user_data["candle_type"] = "CANDLE_1D"
    if text == "WEEKLY":
        context.user_data["candle_type"] = "CANDLE_1W"
    if text == "MONTHLY":
        context.user_data["candle_type"] = "CANDLE_1M"
    update.message.reply_text(
        "Threshold in %, example:\n>>> 8",
        reply_markup=MARKUPS["only_home"],
    )
    return TRIGGER_CREATION


def process_threshold(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data["threshold"] = text
    update.message.reply_text(
        "Finally, what is the market? Example:\n>>> TSLA",
        reply_markup=MARKUPS["market"],
    )
    return TRIGGER_CREATION


def process_market(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    ticker = None if text == "All markets" else text
    reference = (
        context.user_data["candle_type"]
        if context.user_data["reference"] == "CANDLE"
        else context.user_data["reference"]
    )
    trigger = {
        "ticker": ticker,
        "user_id": context.user_data["user_id"],
        "reference": reference,
        "direction": context.user_data["direction"],
        "threshold": context.user_data["threshold"],
    }
    with database.get_db_session() as session:
        session.add(database.Trigger(**trigger))
        session.commit()
    update.message.reply_text(
        "Trigger created",
        reply_markup=MARKUPS["start"],
    )
    return CHOOSING


def delete_trigger(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Type ID of the trigger, example:\n>>> 1",
        reply_markup=MARKUPS["only_home"],
    )
    return TRIGGER_DELETION


def process_trigger_idx(update: Update, context: CallbackContext) -> int:
    trigger_idx = int(update.message.text) - 1
    user_id = context.user_data["user_id"]
    with database.get_db_session() as session:
        triggers = utils.get_user_triggers(user_id, session)
        trigger = triggers[trigger_idx]
        session.query(database.Trigger).filter(
            database.Trigger.id == trigger.id
        ).delete()
        update.message.reply_text(
            "Deleted",
            reply_markup=MARKUPS["start"],
        )
        return CHOOSING


def get_alerts(update: Update, context: CallbackContext) -> int:
    user_id = context.user_data["user_id"]
    with database.get_db_session() as session:
        alerts = utils.get_user_alerts(user_id, session)
        if not alerts:
            update.message.reply_text(
                "You don't have alerts",
                reply_markup=MARKUPS["start"],
            )
            return CHOOSING
        else:
            message = ""
            for i, alert in enumerate(alerts):
                message += format_alert(i, alert, session)
            update.message.reply_text(
                f"Here is a list of recent alerts:\n{message}",
                reply_markup=MARKUPS["start"],
            )
            return CHOOSING


def home(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    update.message.reply_text(
        "Conversation ended", reply_markup=MARKUPS["new_conversation"]
    )
    user_data.clear()
    return ConversationHandler.END


def main(mode: schemas.ServerStartMode) -> None:
    updater = Updater(settings.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    states = {
        USER_CREATION: [
            MessageHandler(Filters.regex(r"^(No)$"), home),
            MessageHandler(Filters.regex(r"^(Yes)$"), request_token),
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex(r"^Home$")),
                create_user,
            ),
        ],
        CHOOSING: [
            MessageHandler(Filters.regex(r"^(Positions)$"), get_positions),
            MessageHandler(Filters.regex(r"^(Triggers)$"), get_triggers),
            MessageHandler(Filters.regex(r"^(Alerts)$"), get_alerts),
            MessageHandler(Filters.regex(r"^(Status)$"), status),
        ],
        TRIGGERS: [
            MessageHandler(Filters.regex(r"^(Create trigger)$"), create_trigger),
            MessageHandler(Filters.regex(r"^(Delete trigger)$"), delete_trigger),
        ],
        TRIGGER_CREATION: [
            MessageHandler(Filters.regex(r"^(Increase|Decrease)$"), process_direction),
            MessageHandler(
                Filters.regex(r"^(Portfolio)$"), process_portfolio_reference
            ),
            MessageHandler(Filters.regex(r"^(Candle)$"), process_candle_reference),
            MessageHandler(
                Filters.regex(r"^(Daily|Weekly|Monthly)$"), process_candle_type
            ),
            MessageHandler(Filters.regex(r"^(\d+(\.\d+)?)$"), process_threshold),
            MessageHandler(
                Filters.text & ~(Filters.command | Filters.regex(r"^Home$")),
                process_market,
            ),
        ],
        TRIGGER_DELETION: [
            MessageHandler(Filters.regex(r"^(\d+(\.\d+)?)$"), process_trigger_idx),
        ],
    }
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states=states,
        fallbacks=[MessageHandler(Filters.regex("^Home$"), home)],
    )
    dispatcher.add_handler(conv_handler)
    if mode == schemas.ServerStartMode.WEBHOOK:
        updater.start_webhook(listen="0.0.0.0", port=5000, url_path=settings.BOT_TOKEN)
        updater.bot.setWebhook(
            f"{settings.SERVER_IP}/{settings.BOT_TOKEN}",
            certificate=open(settings.CERTIFICATE, "rb"),
        )
    else:
        updater.start_polling()
        print(">> Bot started")
        updater.idle()


if __name__ == "__main__":
    mode = schemas.ServerStartMode.POLLING
    if len(sys.argv) == 2:
        mode = schemas.ServerStartMode[sys.argv[1].upper()]
    main(mode)
