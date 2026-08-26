def classFactory(iface):
    from .postgres_connector import PostgreSQLConnector
    return PostgreSQLConnector(iface)