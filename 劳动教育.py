import json
import time

import requests


class App:
    def __init__(self):
        self.username = input("Username:")
        self.password = "AXy@321987"
        # self.password = "Zxy20041001@"
        self.sess = requests.session()
        self.headers = self.getCookie()
        self.downCode()
        self.login()
        data = self.payload()
        self.currentSemesterId = data[0]
        self.kv = data[1]
        print(self.currentSemesterId, self.kv, sep="\t")

    def getCookie(self) -> dict:
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/home/school_info"
        headers = {
            "Sec-Ch-Ua-Platform": "Windows",
            "content-type": "application/json",
            "origin": "https://kkzxsx.cqcst.edu.cn",
            "accept": "application/json, text/plain, */*",
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }
        r = self.sess.get(url=url, headers=headers)
        headers["cookie"] = r.cookies.keys()[0] + "=" + r.cookies.get("SESSION")
        print("获取Cookie成功")
        return headers

    def downCode(self) -> None:
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/Kaptcha?"
        r = self.sess.get(url=url, headers=self.headers)
        with open("./code.jpg", "wb+") as fp:
            fp.write(r.content)
            print("验证码下载成功")

    def login(self) -> None:  # AXy@321987
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/auth"
        code = input("请输入验证码：")
        data = {
            "account": self.username,
            "code": code,
            "password": self.password
        }
        r = self.sess.post(url=url, data=json.dumps(data), headers=self.headers)
        if r.json()["msg"] == "成功":
            print(f'{r.json()["data"]["realName"]} 登陆成功')
            # print('登陆成功')
        try:
            self.headers["cookie"] = self.headers["cookie"] + ";Member-schoolId=0;" + "Member-Token=" + r.headers[
                "Member-Token"]
            self.headers["member-token"] = r.headers["member-token"]
            # print(self.headers)
        except KeyError:
            print("验证码错误")

    def getId(self) -> int:
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/course/study/my"
        data = {"page": 1,
                "pageSize": 15,
                "status": 1
                }
        r = self.sess.post(url=url, headers=self.headers, data=json.dumps(data))
        return r.json()["data"]["lists"][0]["courseId"]
        # return 619

    def payload(self) -> tuple:
        kv = {}
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/home/course_detail"
        data = {"id": self.getId()}
        r = self.sess.post(url=url, data=json.dumps(data), headers=self.headers)
        currentSemesterId = r.json()["data"]["currentSemesterId"]
        chapters = r.json()["data"]["chapters"]
        for chapter in chapters:
            sections = chapter["sections"]
            for section in sections:
                sectionId = section["id"]
                progress = section["videoDuration"]
                kv[sectionId] = progress
        return currentSemesterId, kv

    def submit(self) -> None:
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/report/submit"
        try:
            r = self.sess.get(url=url, headers=self.headers, timeout=10)
            try:
                print(r.json())
            except:
                print("出错了")
        except requests.exceptions.ReadTimeout:
            print("连接超时")
            time.sleep(1)

    def run(self) -> None:
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/course/study/upload/progress"
        for k, v in self.kv.items():
            print(k)
            self.submit()
            try:
                data = {
                    "position": v,
                    "sectionId": str(k),
                    "semesterId": self.currentSemesterId
                }
                r = self.sess.post(url=url, data=json.dumps(data), headers=self.headers, timeout=10)
            except:
                v -= 1
                data = {
                    "position": v,
                    "sectionId": k,
                    "semesterId": self.currentSemesterId
                }
                r = self.sess.post(url=url, data=json.dumps(data), headers=self.headers, timeout=10)
            print(r.json())
            self.submit()
            # time.sleep(0.5)

    def run_test(self):
        url = "https://kkzxsx.cqcst.edu.cn/api/v1/course/study/upload/progress"
        for i in range(3, 264, 3):
            time.sleep(1)
            data = {
                "position": i,
                "sectionId": 13940,
                "semesterId": self.currentSemesterId
            }
            r = self.sess.post(url=url, data=json.dumps(data), headers=self.headers, timeout=10)
            print(r.json())


if __name__ == '__main__':
    app = App()
    app.run()
    # app.run_test()
