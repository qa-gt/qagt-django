import logging

import pymysql

pymysql.install_as_MySQLdb()

logger = logging.getLogger("log")


def get_extra(request, null=True):
    return {
        "req_path":
        null and request.path,
        "req_ip":
        null and request.ip,
        "req_user":
        null and
        (request.session.get("user", 0) if hasattr(request, "session") else 0),
        "req_method":
        null and request.method,
    }
