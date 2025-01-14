import json
import typing
import mongoengine

import harmony_models.verify as verify_models
import harmony_models.feedback as feedback_models

with open("config.json", "r") as f:
    config = json.load(f)

db_name = config["db"]["db_name"]
db_host = config["db"]["hostname"]
db_port = config["db"]["port"]
db_username = config["db"]["username"]
db_password = config["db"]["password"]

try:
    db_replica_set = config["db"]["replica_set_name"]
except KeyError:
    db_replica_set = None

_mongodb_connection_string = f"mongodb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

if db_replica_set:
    _mongodb_connection_string += f"?replicaSet={db_replica_set}"

connection = mongoengine.connect(
    host=_mongodb_connection_string
)


def get_pending_verification(discord_user_id: int) -> typing.Optional[verify_models.PendingVerification]:
    """
    Fetch a pending verification from the database.
    :param discord_user_id: The Discord user to fetch the pending verification for.
    :return: The pending verification, if found, otherwise None.
    """
    return verify_models.PendingVerification.objects(discord_user__discord_user_id=discord_user_id).first()


def has_pending_verification(discord_user_id: int) -> bool:
    """
    Check if a Discord user has a pending verification.
    :param discord_user_id: The user ID to check.
    :return: True if the user has a pending verification, otherwise False.
    """
    return get_pending_verification(discord_user_id) is not None


def get_verification_data(discord_user_id: int = None,
                          reddit_username: str = None) -> typing.Optional[verify_models.VerifiedUser]:
    """
    Fetch a Discord user's verification data from the database.
    :param discord_user_id: The Discord user ID to fetch the verification for.
    :param reddit_username: The Reddit username to fetch the verification for.
    :return: The verification data, if found, otherwise None.
    """
    if discord_user_id:
        return verify_models.VerifiedUser.objects(discord_user__discord_user_id=discord_user_id).first()
    if reddit_username:
        return verify_models.VerifiedUser.objects(reddit_user__reddit_username__iexact=reddit_username).first()

    return None


def get_all_verification_data() -> typing.List[verify_models.VerifiedUser]:
    """
    Fetch all verified users.
    :return: A list of all verified users.
    """
    return verify_models.VerifiedUser.objects()


def has_verification_data(discord_user_id: int) -> bool:
    """
    Check if a Discord user has verification data.
    :param discord_user_id: The user ID to check.
    :return: True if the user has verification data, otherwise False.
    """
    return get_verification_data(discord_user_id=discord_user_id) is not None


def get_feedback_data(message_id: int) -> typing.Optional[feedback_models.FeedbackItem]:
    """
    Fetch feedback data by the message ID containing its voting view.
    :param message_id: The message ID to fetch.
    :return: The feedback item, if it exists.
    """
    return feedback_models.FeedbackItem.objects(discord_message_id=message_id).first()


def delete_feedback_data(message_id: int) -> typing.NoReturn:
    """
    Delete feedback data by the message ID containing its voting view.
    :param message_id: The feedback data to delete, by the Discord message ID containing its voting view.
    :return: Nothing.
    """
    feedback_data = get_feedback_data(message_id)

    if feedback_data:
        feedback_data.delete()
