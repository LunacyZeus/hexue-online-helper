import asyncio
import json
import os
import time

import httpx
import jmespath
from DrissionPage._pages.chromium_page import ChromiumPage
from DrissionPage._pages.chromium_tab import ChromiumTab
from loguru import logger
from sympy import Union
from alive_progress import alive_bar

from utils.dp import get_page, record_data


class MainProcess(object):
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.page: ChromiumPage = None

    async def start_dp(self):
        debugger_port = 12345
        self.page = get_page(debugger_port=debugger_port)

    def help_study(self,tab=None):
        '''
        帮助学习函数
        :return:
        '''
        if tab:
            page = tab
        else:
            page = self.page

        if '/#/cours-study' not in page.url:
            logger.error("请在课程学习界面使用")
            input('-->')

        introduce_info_ele = page(f"x://div[@class='introduce_info']")
        kc_title = introduce_info_ele.ele(f"x://p[@class='info_title']").text

        study_Progress_ele = page(f"x://div[@class='study_Progress']")
        progressbar_ele = study_Progress_ele.child('tag:div')
        xx_jd = progressbar_ele.attr('aria-valuenow')
        logger.debug(f"开始获取当前课程->{kc_title} 总学习进度:{xx_jd}%")

        logger.debug('点击继续学习按钮')
        info_list_button = page(f"x://div[@class='info_list_button']")
        #print(info_list_button.html)
        tab = info_list_button.click.for_new_tab()
        time.sleep(1)

        self.help_study_detail(tab=tab)

        logger.debug(f"学习结束 跳转到课程列表后操作")
        self.handle_cours_study()

    def help_study_detail(self, tab):
        logger.debug(f"当前学习页面->{tab.url}")

        xx_title_ele = tab(f"x://p[@class='top_p']")
        xx_title = xx_title_ele.text
        logger.debug(f"当前学习标题->{xx_title}")

        if tab.wait.ele_loaded('tag:video', timeout=3):
            logger.debug(f"出现视频标签")
            video_ele = tab.ele("tag:video")
            logger.debug(f"开始获取视频进度")
            while 1:
                progress_holder_div = tab(f"x://div[contains(@class, 'vjs-progress-holder') and contains(@class, 'vjs-slider')]")
                valuetext = progress_holder_div.attr('aria-valuetext')
                valuenow = progress_holder_div.attr('aria-valuenow')
                logger.debug(f"[{xx_title}] 当前学习进度:{valuenow} 进度条时间:{valuetext}")
                if valuenow == '100.00':
                    logger.error(f"[{xx_title}] 学习视频结束 开始切换到下一个课程")
                    logger.debug(f"关闭当前页面")
                    #tab.close()
                    break
                time.sleep(5)
        else:
            logger.error("没找到video视频标签 疑似为ppt 等待一分钟后关闭网页")

            time.sleep(3)

            # 使用 with 语句创建一个进度条
            with alive_bar(force_tty=True) as bar: # 给 alive_bar 传入进度条总数目（这里是 100）
                for item in range(500):
                    # 等待 1s
                    time.sleep(0.1)
                    #更新进度条，进度 +1
                    bar()

        logger.debug("点击退出学习按钮")
        tc_btn_xpath = "//button[@class='el-button el-button--default is-plain']"
        tc_btn = tab(f"x:{tc_btn_xpath}")
        tc_btn.click()
        time.sleep(1)
        logger.debug("点击退出学习按钮结束")
        qd_span = tab(f"x://span[contains(text(), '确 定')]")
        qd_span.click()
        logger.debug("点击确定按钮")
        tab.close()

    def handle_cours_study(self):#获取学习列表页界面并自动点击继续学习
        cours_study_tab = self.page.get_tab(url="/#/cours-study")
        logger.debug(f"刷新并获取学习列表页地址->{cours_study_tab.url}")
        cours_study_tab.refresh()

    async def start_login(self):
        url = f'https://login.hexuezx.cn/?code=10427'
        self.page.get(url=url)
        logger.debug(f"进入到登录页面 请手动登录")
        input('-->')

    async def run(self):
        await self.start_dp()  # 启动dp框架

        # await self.start_login()#进入到登陆页

        while 1:
            if '/#/cours-study' not in self.page.url:
                logger.error("请在课程学习界面使用")
                input('-->')

            study_Progress_ele = self.page(f"x://div[@class='study_Progress']")
            progressbar_ele = study_Progress_ele.child('tag:div')
            xx_jd = progressbar_ele.attr('aria-valuenow')

            if xx_jd == "100":
                logger.error(f"课程进度已100% 无需学习")
                return

            #input('-->')

            self.help_study()#用这个函数学习

        #self.help_study_detail(self.page)
        #logger.debug(f"学习结束 跳转到课程列表后操作")
        #self.handle_cours_study()

        #self.test()


async def main():
    process = MainProcess()
    await process.run()


def test():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == '__main__':
    test()
