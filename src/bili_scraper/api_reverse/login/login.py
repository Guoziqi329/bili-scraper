import time
import requests
import qrcode
import threading


class Login:
    def __init__(self, session):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
        }
        self.session = session

    @staticmethod
    def showQRCode(url):
        def worker():
            # 生成二维码对象
            qr = qrcode.QRCode(box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)

            # 创建图片并显示
            img = qr.make_image(fill_color="black", back_color="white")
            img.show()

        # 创建并启动线程
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def checkScanQRCode(self, qrcode_key):
        url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
        payload = {
            'qrcode_key': qrcode_key,
            'source': 'main-fe-header',
            'web_location': '333.1007',
            'x-bili-locale-json': '{"c_locale":{"language":"zh","region":"CN"},"always_translate":true}',
            'b_ret': '1wNiAAAAAElFTkSuQmCC//VZIAAAAAAAZJREFUAwAd48MBKGU+zgAAAABJRU5ErkJggg=='
        }
        response = self.session.get(url, params=payload, headers=self.headers)
        print(response.text)
        if response.status_code == 200:
            return response.json()

    def get_user_info(self):
        url = 'https://api.bilibili.com/x/web-interface/nav'
        response = self.session.get(url, headers=self.headers)
        return response.json()

    def get_login_url_AND_qrcode_key(self) -> tuple:
        """
        get login url and qrcode key
        :return: login url, qrcode key
        """
        payload = {
            'source': 'main-fe-header',
            'go_url': 'https://www.bilibili.com/',
            'web_location': '333.1007',
            'x-bili-locale-json': '{"c_locale":{"language":"zh","region":"CN"},"always_translate":true}'
        }
        url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
        response = self.session.get(url, params=payload, headers=self.headers)

        if response.status_code != 200:
            raise "request error"

        login_url, qrcode_key = response.json()['data']['url'], response.json()['data']['qrcode_key']
        return login_url, qrcode_key

    def checkQRCode(self, qrcode_key):
        """
        Check QR code validity
        :param qrcode_key: qrcode key
        :return: code
        """
        response = self.checkScanQRCode(qrcode_key)
        code = response['data']['code']
        print(response['data']['message'])
        return code

    def LoginWithQRCode(self):
        login_url, qrcode_key = self.get_login_url_AND_qrcode_key()

        print(login_url, qrcode_key)

        self.showQRCode(login_url)

        code = 1
        while code:
            code = self.checkQRCode(qrcode_key)
            time.sleep(1)

        print(self.session.cookies)
        print(self.get_user_info())
        return self.session.cookies

    def check_session(self):
        user_info = self.get_user_info()
        if user_info['code'] == 0:
            return True
        return False



if __name__ == '__main__':
    session = requests.session()
    login = Login(session)

    login.LoginWithQRCode()
