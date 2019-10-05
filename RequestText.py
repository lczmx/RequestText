import requests
from bs4 import BeautifulSoup

__verson__ = 1.0
__auth__ = "lczmx"


class GetClassInfo:
    def __init__(self):
        self.url = None
        # 标题
        self.title_info = []
        # 下一页
        self.next_page_info = []
        # 内容
        self.content_info = []
        self.text_name = None
        self.encoding = None
        self.next_page_string = None
        self.html_code_mode = False
        self.soup = None
        self.url = self.check_url("章节url（如：第一章的）>>>")
        self._encoding_list = ["Unicode", "unicode", "ASCII", "ascii", "ISO-8859-1", "iso-8859-1",
                               "UTF-16", "utf-16", "GB18030", "gb18030", "GBK", "gbk", "GB2312",
                               "gb2312", "UTF-8", "utf-8", "utf8"]
        self.get_html()

    def check_url(self, tips):
        while True:
            url = input(tips)
            if not url: continue
            if url.startswith("http://") or url.startswith("https://"):
                return url
            print("url格式错误（http://或https://开头）\n 请重新输入")

    def get_html(self):
        r = requests.get(self.url)
        self.encoding = r.apparent_encoding
        encoding = input("是否修改编码？\n是：输入编码，否：留空\n>>>")
        if encoding:
            if encoding in self._encoding_list:
                print("\n encoding : 从%s ----> %s \n" % (self.encoding, encoding))
                self.encoding = encoding
            else:
                print("“%s”不合法！" % encoding)

                # 仅仅是为了防止输入错误的编码方式， 只有正确就行
                print("目前只支持：", "、".join(self._encoding_list))
                print("\n已经使用自动解析的编码方式")
        else:
            print("使用自动解析的编码方式")
        print("\n当前编码方式 % s\n" % self.encoding)
        r.encoding = self.encoding
        self.get_info(r.text)

    def get_info(self, text):
        s = BeautifulSoup(text, "html.parser")
        self.soup = s.find(name="body")

        self.text_name = input("小说名字>>>")
        title = input("章节标题>>>")
        next_page = input("下一页名字(如：下一页、下一章)>>>")
        self.next_page_string = next_page
        content = input("正文一个自然段(提示：必须一段完整内容，否者写入内容或许有多余部分！)\n>>>")

        self.find(self.soup, title, self.title_info)
        self.find(self.soup, next_page, self.next_page_info)
        self.find(self.soup, content, self.content_info)
        self.check(title, next_page, content)

    def add_to_select_condition(self, ele, modify_list):
        if ele.has_attr("id"):
            modify_list.append("#" + ele.attrs["id"])
        elif ele.has_attr("class"):
            modify_list.append("." + ele.attrs["class"][0])
        else:
            modify_list.append(ele.name)

    def check(self, title, next_page, content):

        if not self.title_info:
            print("\n标题匹配不到， 进入模糊匹配模式......\n")
            self.html_code_mode = True
            self.find(self.soup, title, self.title_info)
            if not self.title_info:
                exit("标题: 模糊匹配模式也匹配不上，请检查输入内容！")
            else:
                print("标题: 使用模糊匹配模式匹配成功\n")

        if not self.next_page_info:
            print("\n下一页标签匹配不到， 进入模糊匹配模式......\n")

            self.html_code_mode = True
            self.find(self.soup, next_page, self.next_page_info)
            if not self.next_page_info:
                exit("下一页：模糊匹配模式也匹配不上，请检查输入内容！")
            else:
                print("下一页: 使用模糊匹配模式匹配成功\n")

        if not self.content_info:
            print("\n内容匹配不到， 进入模糊匹配模式......\n")

            self.html_code_mode = True
            self.find(self.soup, content, self.content_info)
            if not self.content_info:
                exit("内容：模糊匹配模式也匹配不上，请检查输入内容！")
            else:
                print("内容: 使用模糊匹配模式匹配成功\n")

    def find(self, ele, text, in_fo):
        try:
            if text == ele.text.strip():
                return True

            elif self.html_code_mode and text in ele.text and ele.name in ["p", "a", "dd", "span", "h1", "h2", "h3"]:
                return True

            # 以下的检查方法是究极方法， 没有就没办法
            elif self.html_code_mode:
                if text in ele.text and ele.name == "div":
                    br_ele_count = 0
                    for br_ele in ele.children:
                        if br_ele.name == "br":
                            br_ele_count += 1
                    if br_ele_count > 10:
                        return True

                # 乞求写网站的人规范吧
                elif text in ele.text and ele.attrs.get("id") in ["next_page", "title", "content", "contents"]:
                    return True

            for i in ele.children:
                if self.find(i, text, in_fo):
                    self.add_to_select_condition(i, in_fo)
                    return True
        except AttributeError:
            pass


class GetText:
    def __init__(self, url, text_name, title_info, next_page_info, content_info, encoding, next_page_string):
        self.url = url
        self.encoding = encoding
        self.text_name = text_name
        self.title_info = title_info
        self.next_page_info = next_page_info
        self.content_info = content_info
        self.next_page_string = next_page_string
        self.soup = None
        self.title = None
        self.content_list = None
        self.base_url = None
        self.reconnect_count = 1

    def start(self):
        try:
            self.get_html()
            self.reconnect_count = 1
        except Exception as e:
            print(e)
            if self.reconnect_count >= 3:
                exit("重试超过3次，自动退出！！")

            print("正在重试 第%s 次 " % self.reconnect_count)
            self.reconnect_count += 1
            self.start()
        else:
            self.get_title()
            self.get_content()
            self.write()
            self.get_next()

    def get_html(self):
        r = requests.get(self.url, timeout=10)
        r.encoding = self.encoding
        self.soup = BeautifulSoup(r.text, "html.parser")

    def get_title(self):
        self.title = self.soup.select(" ".join(self.title_info[::-1]))[0].text

    def get_content(self):
        self.content_list = self.soup.select(" ".join(self.content_info[::-1]))

    def write(self):
        with open("%s.txt" % self.text_name, "a+", encoding="utf-8") as f:
            f.write(self.title)
            for c in self.content_list:
                f.write("\n")
                f.write(c.text)
            try:
                print("已经写入 %s" % self.title)
            except UnicodeEncodeError:
                print("由于编码问题，跳过本章提示，但不会影响内容。")

    def get_next(self):
        next_ele = None
        ele = self.soup.select(" ".join(self.next_page_info[::-1]))

        for i in ele:
            if i.text == self.next_page_string:
                next_ele = i

        # 没有 下一章标签
        if not next_ele:
            print("\n没有下一章标签\n %s 已经下载完成！" % self.text_name)
            return

        if next_ele.has_attr("href"):
            next_url = next_ele.attrs.get("href")
        else:
            # 没有 href
            print("\n没有 href\n %s 已经下载完成！" % self.text_name)
            return

        if self.check_up(next_url):
            print("\n%s 已经下载完成！" % self.text_name)
            return

        self.start()

    def check_up(self, next_url):

        if next_url.startswith("javascript"):
            print("检测到 next_url 为 javascript\n本爬虫不支持JS页面的爬取，正在停止爬取......")
            return True
        # 究极比对
        if next_url.startswith("http"):
            new_url = next_url
        else:
            if self.base_url.endswith("/"):
                new_url = self.base_url[:-1] + next_url
            else:
                new_url = self.base_url + next_url

        url_list1 = self.url.split("/")[:-1]
        url_list2 = new_url.split("/")[:-1]
        if url_list1 != url_list2:
            print("究极比对未通过")
            return True
        else:
            self.url = new_url


if __name__ == '__main__':
    get_info_obj = GetClassInfo()
    get_text_obj = GetText(get_info_obj.url, get_info_obj.text_name, get_info_obj.title_info,
                           get_info_obj.next_page_info, get_info_obj.content_info, get_info_obj.encoding,
                           get_info_obj.next_page_string)

    get_text_obj.base_url = get_info_obj.check_url("请输入BaseUrl（域名）>>>")
    get_text_obj.start()
