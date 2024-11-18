import json
import os
import sys
import traceback

from DrissionPage._configs.chromium_options import ChromiumOptions
from DrissionPage._pages.chromium_page import ChromiumPage


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print("运行崩溃", e)
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict)

    return wrapper


def record_data(file_path, data, is_parse=False):
    if type(data) == str:
        if is_parse:
            save_data = json.loads(data)
            save_data = json.dumps(save_data, ensure_ascii=False, indent=4)
        else:
            save_data = data
    else:
        save_data = json.dumps(data, ensure_ascii=False, indent=4)

    open(file_path, "w", encoding="utf8").write(save_data)


def get_record_data(file_path, is_json=True):
    data = open(file_path, "r", encoding="utf8").read()
    if is_json:
        data = json.loads(data)

    return data


def get_page(debugger_port=9222) -> ChromiumPage:
    debugger_address = f"127.0.0.1:{debugger_port}"

    options = ChromiumOptions()
    options.set_argument(arg="--remote-allow-origins=*")
    # options.set_timeouts(pageLoad=5)
    options.set_paths(address=debugger_address)
    options.mute()
    # options.set_timeouts(base=25, page_load=15, script=15)

    # page = ChromiumPage(chromium_options=options)
    page = ChromiumPage(addr_or_opts=options)
    return page


def dict2ck(ck_dict):
    cookie_list = [k + "=" + v for k, v in ck_dict.items()]
    cookie = ';'.join(item for item in cookie_list)
    return cookie
