import logging
from math import ceil
import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from .abstract import AbstractDictionary

logger = logging.getLogger('dict2Anki.dictionary.baidu')

# 获取收藏分组
# https://fanyi.baidu.com/pccollgroup?req=list
# https://fanyi.baidu.com/pcnewcollection?req=get

class Baidu(AbstractDictionary):
  name = '百度翻译'
  loginUrl = 'https://fanyi.baidu.com/mtpe-individual/collection'
  timeout = 10
  headers = {
    'Host': 'fanyi.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
  }
  retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
  )
  session = requests.Session()
  session.mount('http://', HTTPAdapter(max_retries=retries))
  session.mount('https://', HTTPAdapter(max_retries=retries))

  def __init__(self):
    self.indexSoup = None
    self.groups = []

  def checkCookie(self, cookie: dict) -> bool:
    """
    cookie有效性检验
    :param cookie:
    :return: bool
    """
    rsp = requests.get(
      'https://fanyi.baidu.com/mtpe/v2/user/getInfo',
      cookies=cookie,
      headers=self.headers
    )
    if rsp.json().get('errno', None) == 0:
      self.indexSoup = BeautifulSoup(rsp.text, features="html.parser")
      logger.info('Cookie有效')
      cookiesJar = requests.utils.cookiejar_from_dict(
        cookie,
        cookiejar=None,
        overwrite=True
      )
      self.session.cookies = cookiesJar
      return True
    logger.info('Cookie失效')
    return False

  @staticmethod
  def loginCheckCallbackFn(cookie, content):
    if 'BDUSS' in cookie and 'BDUSS_BFESS' in cookie:
      return True
    return False

  def getGroups(self) -> [(str, int)]:
    """
    获取单词本分组
    :return: [(group_name,group_id)]
    """
    r = self.session.get(
      url='https://fanyi.baidu.com/pccollgroup?req=list',
      timeout=self.timeout,
    )
    groups = [(g['name'], g['id'], g['type']) for g in r.json()['data']]
    logger.info(f'单词本分组:{groups}')
    self.groups = groups

    return groups

  def getTotalPage(self, groupName: str, groupId: int) -> int:
    """
    获取分组下总页数
    :param groupName: 分组名称
    :param groupId:分组id
    :return:
    """

    try:
      r = self.session.post(
        url='https://fanyi.baidu.com/pcnewcollection?req=get',
        timeout=self.timeout,
        data={
          'currentTotal': 0,
          'direction': 'all',
          'dstStatus': 'all',
          'gid': groupId,
          'order': 'time',
          'page': 1,
          'pageSize': 10,
          'scroll': False,
          'total': 0
        }
      )
      res = r.json()
      totalWords = res['total']
      # totalPages = res['totalpage']
      totalPages = ceil(totalWords / 10)  # 这里按网页默认每页取10个

    except Exception as error:
      logger.exception(f'网络异常{error}')

    else:
      logger.info(f'该分组({groupName}-{groupId})下共有{totalPages}页')
      return totalPages

  def getWordsByPage(self, pageNo: int, groupName: str, groupId: str) -> [str]:
    """
    获取分组下每一页的单词
    :param pageNo: 页数
    :param groupName: 分组名
    :param groupId: 分组id
    :return:
    """

    wordList = []
    try:
      logger.info(f'获取单词本(f{groupName}-{groupId})第:{pageNo}页')
      r = self.session.post(
        'https://fanyi.baidu.com/pcnewcollection?req=get',
        timeout=self.timeout,
        data={
          'currentTotal': 10,
          'direction': 'all',
          'dstStatus': 'all',
          'gid': groupId,
          'order': 'time',
          'page': pageNo,
          'pageSize': 10,
          'scroll': False,
        }
      )
      wordList = [item['fanyisrc'] for item in r.json()['pageinfo']]
    except Exception as e:
      logger.exception(f'网络异常{e}')
    finally:
      logger.info(wordList)
      return wordList
