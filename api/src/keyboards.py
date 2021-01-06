from telegram import ReplyKeyboardMarkup


empty_keyboard = [[]]
new_conversation = [["/start"]]
yes_no_keyboard = [["Yes", "No"]]
start_keyboard = [["Positions", "Triggers", "Alerts", "Status"]]
no_triggers_keyboard = [["Create trigger"], ["Home"]]
triggers_keyboard = [["Create trigger", "Delete trigger"], ["Home"]]
direction_keyboard = [["Increase", "Decrease"], ["Home"]]
reference_keyboard = [["Portfolio", "Candle"], ["Home"]]
candle_keyboard = [["Daily", "Weekly", "Monthly"], ["Home"]]
only_home_keyboard = [["Home"]]
market_keyboard = [["All markets"], ["Home"]]

MARKUPS = {
    "new_conversation": ReplyKeyboardMarkup(new_conversation, one_time_keyboard=True),
    "market": ReplyKeyboardMarkup(market_keyboard, one_time_keyboard=True),
    "only_home": ReplyKeyboardMarkup(only_home_keyboard, one_time_keyboard=True),
    "candle": ReplyKeyboardMarkup(candle_keyboard, one_time_keyboard=True),
    "reference": ReplyKeyboardMarkup(reference_keyboard, one_time_keyboard=True),
    "direction": ReplyKeyboardMarkup(direction_keyboard, one_time_keyboard=True),
    "triggers": ReplyKeyboardMarkup(triggers_keyboard, one_time_keyboard=True),
    "no_triggers": ReplyKeyboardMarkup(no_triggers_keyboard, one_time_keyboard=True),
    "yes_no": ReplyKeyboardMarkup(yes_no_keyboard, one_time_keyboard=True),
    "start": ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True),
    "empty": ReplyKeyboardMarkup(empty_keyboard, one_time_keyboard=True),
}