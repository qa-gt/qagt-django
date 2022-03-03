function Sign(list, scene = "default") {
    const LIM = {
        "default": {
            1: 1,
            10: 8,
            60: 30,
            300: 100,
            600: 150,
            1800: 300,
            3600: 400,
        },
        "login": {
            5: 1,
        },
        "article": {
            60: 1,
            300: 3,
            600: 5,
            1800: 6,
            3600: 7,
        },
        "comment": {
            5: 1,
            15: 2,
            30: 3,
            60: 5,
            300: 10,
            1200: 20,
            3600: 30,
        },
        "edit_information": {
            60: 1,
            300: 3,
            600: 5,
            3600: 6,
        },
        "test": {
            1: 1,
            600: 2,
        }
    };
    // 校验
    if (typeof (window) === "undefined" || window === null) { return undefined; }
    // if (window.location.hostname != "qa.yxzl.top") {return undefined;}
    if (typeof (list) === "undefined" || list === null || LIM[scene] === undefined) { return undefined; }
    if (window.localStorage.getItem("req_" + scene) === null) {
        window.localStorage.setItem("req_" + scene, JSON.stringify([]));
    }

    // 确认请求次数
    let req = JSON.parse(window.localStorage.getItem("req_" + scene)), now = parseInt(new Date().getTime() / 1000);
    let lim = LIM[scene];
    for (let i in lim) {
        i = parseInt(i);
        if (lim[i] > req.length) { break; }
        if (req[req.length - lim[i]] + i > now) {
            alert(`请求过于频繁，当前场景提交限制为每${i}秒${lim[i]}次。`);
            return undefined;
        }
    }

    // 生成
    let result = "";
    for (let i = 0; i < list.length; i++) {
        result = result + md5(btoa(md5(String(list[i]))));
    }
    result = result + scene;

    // 记录请求
    now -= 86400;
    while (req[0] < now) req.shift();
    req[req.length] = parseInt(new Date().getTime() / 1000);
    window.localStorage.setItem("req_" + scene, JSON.stringify(req));
    return md5(result);
}