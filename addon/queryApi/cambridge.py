import logging
import requests
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from .abstract import AbstractQueryAPI
from bs4 import BeautifulSoup

logger = logging.getLogger('dict2Anki.queryApi.cambridge')
__all__ = ['API']


class Parser:
  def __init__(self, html, term):
    self._soap = BeautifulSoup(html, 'html.parser')
    self.term = term

  @staticmethod
  def __fix_url_without_http(url):
    if url[0:2] == '//':
      return 'https:' + url
    else:
      return url

  @property
  def definition(self) -> list:
    """定义"""
    ret = []
    # $($('.pr.entry-body__el')[0]).find('.pos-body').find('.pr.dsense:nth-child(1) .def-block.ddef_block:nth-child(1) .def-body.ddef_b [lang="zh-Hans"]:nth-child(1)').text()
    # trans dtrans dtrans-se
    # $($('.pr.entry-body__el')[1]).find('.posgram.dpos-g').find('.pos.dpos').text()
    els = self._soap.select('.pr.entry-body__el')
    if not els:
      return ret
    # div = div[0]
    # els = div.select('li') # 多词性
    # if not els: # 单一词性
    #   els = div.select('.exp')
    # if not els: # 还有一奇怪的情况，不在任何的标签里面
    #   trans = div.find(id='trans')
    #   trans.replace_with('') if trans else ''

    #   script = div.find('script')
    #   script.replace_with('') if script else ''

    #   for atag in div.find_all('a'): # 赞踩这些字样
    #     atag.replace_with('')
    #   els = [div]
    # try {

    # }
    try:
      for el in els:
        v = el.select('.posgram.dpos-g .pos.dpos')[0].get_text(strip=True)
        v = v+'.'
        textEl = el.select('.pos-body .pr.dsense:nth-child(1) .def-block.ddef_block:nth-child(1) .def-body.ddef_b [lang="zh-Hans"]:nth-child(1)')
        if textEl:
          t = textEl[0].get_text(strip=True)
        else:
          t =''
        ret.append(v+' ' + t)
    except (KeyError, IndexError):
      pass

    return ret

  @property
  def pronunciations(self) -> dict:
    """发音"""
    url = 'https://api.frdic.com/api/v2/speech/speakweb?'
    pron = {
      'AmEPhonetic': None,
      'AmEUrl': None,
      'BrEPhonetic': None,
      'BrEUrl': None
    }
    els = self._soap.select('.pr.entry-body__el')

    # pron dpron
    # els = self._soap.select('.phonitic-line')
    if not els:
      return pron

    el = els[0]
    ukEl = el.select('.uk.dpron-i')
    usEl = el.select('.us.dpron-i')

    try:
      pron['BrEPhonetic'] = ukEl[0].select('.pron.dpron')[0].get_text(strip=True)
    except (KeyError, IndexError):
      pass

    try:
      url = ukEl[0].select('audio [type="audio/mpeg"]')[0].attrs['src']
      pron['BrEUrl'] = "https://dictionary.cambridge.org{}".format(url)
    except (TypeError, KeyError, IndexError):
      pass

    try:
      pron['AmEPhonetic'] = usEl[0].select('.pron.dpron')[0].get_text(strip=True)
    except (KeyError, IndexError):
      pass

    try:
      url = usEl[0].select('audio [type="audio/mpeg"]')[0].attrs['src']
      pron['AmEUrl'] = "https://dictionary.cambridge.org{}".format(url)
    except (TypeError, KeyError, IndexError):
      pass

    return pron

  @property
  def BrEPhonetic(self) -> str:
    """英式音标"""
    return self.pronunciations['BrEPhonetic']

  @property
  def AmEPhonetic(self) -> str:
    """美式音标"""
    return self.pronunciations['AmEPhonetic']

  @property
  def BrEPron(self) -> str:
    """英式发音url"""
    return self.pronunciations['BrEUrl']

  @property
  def AmEPron(self) -> str:
    """美式发音url"""
    return self.pronunciations['AmEUrl']

  @property
  def sentence(self) -> list:
    ret = []
    # els = self._soap.select('div #ExpLJChild .lj_item')
    # for el in els:
    #   try:
    #     line = el.select('p')
    #     sentence = "".join([ str(c) for c in line[0].contents])
    #     sentence_translation = line[1].get_text(strip=True)
    #     ret.append((sentence, sentence_translation))
    #   except KeyError as e:
    #     pass
    return ret

  @property
  def image(self) -> str:
    ret = None
    # els = self._soap.select('div .word-thumbnail-container img')
    # if els:
    #   try:
    #     img = els[0]
    #     if 'title' not in img.attrs:
    #       ret = self.__fix_url_without_http(img['src'])
    #   except KeyError:
    #     pass
    return ret

  @property
  def phrase(self) -> list:
    ret = []
    # els = self._soap.select('div #ExpSPECChild #phrase')
    # for el in els:
    #   try:
    #     phrase = el.find('i').get_text(strip=True)
    #     exp = el.find(class_='exp').get_text(strip=True)
    #     ret.append((phrase, exp))
    #   except AttributeError:
    #     pass
    return ret

  @property
  def result(self):
    return {
      'term': self.term,
      'definition': self.definition,
      'phrase': self.phrase,
      'image': self.image,
      'sentence': self.sentence,
      'BrEPhonetic': self.BrEPhonetic,
      'AmEPhonetic': self.AmEPhonetic,
      'BrEPron': self.BrEPron,
      'AmEPron': self.AmEPron
    }

class API(AbstractQueryAPI):
  name = '剑桥词典 API'
  timeout = 10
  headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Host': 'dictionary.cambridge.org'
  }
  retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
  session = requests.Session()
  session.mount('http://', HTTPAdapter(max_retries=retries))
  session.mount('https://', HTTPAdapter(max_retries=retries))
  # url = 'https://dictionary.cambridge.org/zhs/%E8%AF%8D%E5%85%B8/%E8%8B%B1%E8%AF%AD-%E6%B1%89%E8%AF%AD-%E7%AE%80%E4%BD%93/{}'
  url = 'https://dictionary.cambridge.org/us/dictionary/english-chinese-simplified/{}'
  parser = Parser

  @classmethod
  def query(cls, word) -> dict:
    queryResult = None

    try:
      rsp = cls.session.get(cls.url.format(word), headers=cls.headers, timeout=cls.timeout)
      logger.debug(f'code:{rsp.status_code}- word:{word} text:{rsp.text[:100]}')
      queryResult = cls.parser(rsp.text, word).result
    except Exception as e:
      logger.exception(e)
    finally:
      logger.debug(queryResult)
      return queryResult
