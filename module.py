from lxml import etree
import requests
import hashlib
import urllib.parse
import json
import zlib
import miniamf.amf3
import base64


class BurstGunAssaultXml:
    def __init__(self, xml_data: bytes):
        self.root = etree.fromstring(xml_data)
        self.datalist = self.root.findall('s')[0].findall('s')

    def get_path(self, name, path):
        for el in self.get_path_data(path):
            if el.attrib['name'] == name:
                return etree.ElementTree(self.root).getpath(el)

    def get_path_data(self, path, sole: bool = True):
        if sole:
            return self.root.xpath(path)[0]
        else:
            return self.root.xpath(path)

    def get_list(self, path, type):
        if type == 'name':
            return [el.attrib['name'] for el in self.get_path_data(path)]
        elif type == 'list':
            return [el for el in self.get_path_data(path)]

    def get_object_number(self, path):
        return len(self.get_path_data(path))

    def export(self):
        return etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='utf-8').decode('utf-8')


class BurstGunAssaultObject:
    def __init__(self, xml_data, path):
        self.xml = BurstGunAssaultXml(etree.tostring(xml_data))
        self.path = path

    def get_value(self, name):
        return self.xml.get_path_data(self.xml.get_path(name, '/s'))

    def revise(self, dict_data: dict, xml):
        # dict_data:{'name':'value'}
        for k, v in dict_data.items():
            dir = xml.get_path_data(self.path)
            for i in dir:
                if i.attrib['name'] == k:
                    i.text = str(v)


def Get_md5(data):
    md5 = hashlib.md5()
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def Get_uid(username):
    url = ('http://cz.4399.com/get_role_info.php?ac=cuid&uname=' + username)
    redata = requests.get(url)
    return redata.text


def Get_gamekey(gameid):
    str0 = Get_md5(Get_md5((gameid + 'LPislKLodlLKKOSNlSDOAADLKADJAOADALAklsd') + gameid))
    return str0[4:20]


def Get_Cookie(user, password):
    url = "http://ptlogin.4399.com/ptlogin/login.do?v=1"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586"}
    postdata = {"username": user, "password": password}
    redata = requests.post(url=url, data=postdata, headers=header)
    return redata.cookies


def Get_Cookie_ByYueying(Username, Password, InputCaptcha):
    return requests.request("POST", "http://ptlogin.4399.com/ptlogin/login.do?v=1",
                            data="loginFrom=uframe&postLoginHandler=default&layoutSelfAdapting=true&externalLogin=qq&displayMode=popup&layout=vertical&appId=www_home&gameId=&css=&redirectUrl=&sessionId=&mainDivId=popup_login_div&includeFcmInfo=false&userNameLabel=4399%E7%94%A8%E6%88%B7%E5%90%8D&userNameTip=%E8%AF%B7%E8%BE%93%E5%85%A54399%E7%94%A8%E6%88%B7%E5%90%8D&welcomeTip=%E6%AC%A2%E8%BF%8E%E5%9B%9E%E5%88%B04399&username=" + Username + "&password=" + Password + "&inputCaptcha=" + InputCaptcha,
                            headers={'Content-type': "application/x-www-form-urlencoded"}).cookies.get_dict()


def Get_Verify(index, data, title, gamekey, uid, gameid):
    str0 = Get_md5(Get_md5(Get_md5(
        "SDALPlsldlnSLWPElsdslSE" + index + gamekey + data + urllib.parse.unquote(title) + uid + gameid + "PKslsO")))
    return str0


def Get_Savelist(Cookie, uid, gameid):
    Gamekey = Get_gamekey(gameid)
    Verify = Get_Verify('', '', '', Get_gamekey(gameid), uid, gameid)
    data = {"uid": uid, "verify": Verify, "gameid": gameid, "gamekey": Gamekey}
    url = "https://save.api.4399.com/?ac=get_list"
    print(data)
    redata = requests.post(url, data=data, cookies=Cookie)
    return redata.text


def Get_Session(gamekey, uid, gameid):
    url = "http://save.api.4399.com/?ac=get_session"
    verify = Get_md5(Get_md5(Get_md5("SDALPlsldlnSLWPElsdslSE" + gamekey + uid + gameid + "PKslsO")))
    data = {"uid": uid, "gamekey": gamekey, "verify": verify, "gameid": gameid}
    redata = requests.post(url, data=data)
    return redata.text


def Get_SaveData(uid, gameid, index, format):
    Gamekey = Get_gamekey(gameid)
    url = "https://save.api.4399.com/ranging.php/?ac=get"
    Verify = Get_md5(
        Get_md5(Get_md5("SDALPlsldlnSLWPElsdslSE" + index + Gamekey + uid + gameid + "PKslsO")))
    data = {"gameid": gameid, "verify": Verify, "gamekey": Gamekey, "index": index, "uid": uid}
    redata = requests.post(url, data=data)
    if (format == "Yes"):
        formatdata = json.loads(redata.text)
        return formatdata["data"]
    return redata.text.encode()


def Save(index, data, title, user, password, gameid):
    url = "http://save.api.4399.com/?ac=save"
    uid = Get_uid(user)
    Gamekey = Get_gamekey(gameid)
    Verify = Get_Verify(index, data, title, Gamekey, uid, gameid)
    Session = Get_Session(Gamekey, uid, gameid)
    httpdata = {"index": index, "data": data, "gamekey": Gamekey, "verify": Verify, "gameid": gameid, "uid": uid,
                "title": title.encode("utf-8"), "session": Session}
    redata = requests.post(url, data=httpdata, cookies=Get_Cookie(user, password))
    if redata.text == "1":
        return "Yes"
    else:
        return redata.text


def Get_RankingByPage(Gameid, Uid, Rid, Page, Cookie):
    url = "http://save.api.4399.com/rank/FlashScoreApi"
    payload = b'\x80\x01\x00\x01\x00\x00\x00\x10getRankingByPage\x00\x00\x00\x00\x0c\x00\x01\x0b\x00\x01\x00\x00\x00\n' + Uid.encode() + b'\x0b\x00\x02\x00\x00\x00\t' + bytes(
        Gameid,
        encoding="utf-8") + b'\x00\x08\x00\x02\x00\x00' + int(
        Rid).to_bytes(2, "big") + b'\x08\x00\x03\x00\x00\x00\n\x08\x00\x04\x00\x00\x00' + int(Page).to_bytes(2,

                                                                                                             "little") + b'\x00'
    headers = {'Content-type': "application/x-thrift", 'Accept': '*/*', 'Accept-Language': 'zh-CN',
               'User-Agent': "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
               'Referer': "https://save.api.4399.com/rank/FlashScoreApi"}
    response = requests.request(method="POST", url=url, headers=headers, data=payload,
                                cookies=Cookie)
    return response.text


def decodeData(data):
    a = miniamf.amf3.ByteArray()
    a.append(zlib.decompress(base64.b64decode((data.encode()))))
    return a.readObject()


def encodeData(data):
    a = miniamf.amf3.ByteArray()
    a.writeObject(data)
    return base64.b64encode(zlib.compress(a.encode()))
