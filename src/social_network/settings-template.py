

PASSWORD_FORMAT_POLICY = dict(
    ONLY_ASCII = False,
    VARIETY_LEN = 8,
    MIN_LEN = 8,
    MAX_LEN = None,
    CONTAINS_UPPER = True,
    CONTAINS_LOWWER = True,
    CONTAINS_NUMBERS = True,
    CONTAINS = "@#$%^*!~"
)


DATABASE = dict(
    DRIVER = "mysql+mysqlconnector",
    HOST = "",
    USER = "",
    PASSWORD = "",
    NAME = ""
)


JWT_TOKEN_POLICY = dict(
    TOKEN_EXPIRES_IN=3600,
    REFRESH_TOKEN_EXPIRES_IN=259200,
    SECRET = "",
    ALGORITM = "HS256"
)


PAGINATION_POLICY = dict(
    LIMIT=25
)


class Config:
    ENV = "develompment"
    DEBUG = True
    LOGGING_SETTINGS = ""

    DATABASE = DATABASE
    PASSWORD_FORMAT_POLICY = PASSWORD_FORMAT_POLICY
    JWT_TOKEN_POLICY = JWT_TOKEN_POLICY
    PAGINATION_POLICY = PAGINATION_POLICY



    
