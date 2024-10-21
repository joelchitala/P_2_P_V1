from enum import Enum


class ClientCommands(Enum):
    EXIT = "-c exit"
    HELP = "-c help"

    #SEND
    SEND_TEXT = "-c send:text"

    # Query
    QUERY_ADD = "query_add"
    QUERY_REMOVE = "query_remove"