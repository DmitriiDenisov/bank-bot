import bcrypt


def get_hash(plain_text_password: str) -> str:
    """
    Hash a password for the first time. Using bcrypt, the salt is saved into the hash itself
    :param plain_text_password: str, password of customer
    :return: str, hashed with salt password
    """
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_hash(plain_text_password: str, hashed_password: str) -> bool:
    """
    Checks hashed password. Using bcrypt, the salt is saved into the hash itself
    :param plain_text_password: str, password of a customer
    :param hashed_password: hashed password of customer
    :return: bool, True if hash(plain_text_password)=hashed_password
    """
    return bcrypt.checkpw(plain_text_password, hashed_password)


