import logging

import pymysql

pymysql.install_as_MySQLdb()

logger = logging.getLogger("log")


def get_extra(request):
    return {
        "req_path": request.path,
        "req_ip": request.ip,
        "req_user": request.session.get("user", 0) if hasattr(request, "session") else 0,
        "req_method": request.method,
    }
