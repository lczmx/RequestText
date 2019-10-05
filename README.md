# RequestText
可以爬取市面上绝大部分的非JS构成的页面
功能：
  1、能根据输入必须的信息确定筛选的条件
  2、对于特殊的难以自动推断出筛选的条件的可以手动输入
  3.适合于一本一本的下载小说用
  4、可以配置好配置文件多线程的自动爬取多本小说（需要自定制）

环境：
  python3
  requests库
  BeautifulSoup4库
  

注：此脚本仅供学习使用，请勿商业使用，否者后果自负！

使用方式：
只需要使用命令行: 
  Windows：
      python RequestText.py
      
      
  Linux:
      python3 RequestText.py
  根据提示输入必须的信息即可爬取小说
  
  提示：请确认python是否已经加到环境变量中

下载完后的小说存放于当前目录下
