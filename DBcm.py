import mysql.connector


class ConnectionError(Exception):
    pass


class CredentialsError(Exception):
    pass


class SQLError(Exception):
    pass

class OperationalError(Exception):
    pass

class UseDatabase:
    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self) -> 'cursor':
        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialsError(err)
        except mysql.connector.errors.OperationalError as err:
            raise OperationalError(err)

    def __exit__(self, exec_type, exc_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exec_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exec_type:
            raise SQLError(exc_value)
