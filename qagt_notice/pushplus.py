import threading
import time

import requests
from QAGT import get_extra, logger


def send_push(user):
    time.sleep(1000)
    count = user.notices.filter(state=0).count()
    if count == 0:
        logger.info(f"{user} 没有未读消息, 取消推送", extra=get_extra(user, null=""))
        return
    try:
        requests.post("http://www.pushplus.plus/send",
                      data={
                          "token": user.token,
                          "title": f"你有{count}条新消息",
                          "content": f"你有{count}条新消息，请登录QA瓜田官网查看",
                      })
        user.notices.filter(state=0).update(state=1)
        logger.info(f"{user} 推送成功{count}条消息", extra=get_extra(user, null=""))
    except Exception as e:
        print(e)


def make_push(request, user):
    if not user.notices.filter(state=0).exists() or not user.pushplus_token:
        return
    logger.info(f"创建了 {user} 的推送任务", extra=get_extra(request))
    threading.Thread(target=send_push, args=(user, )).start()
