from abc import ABC, abstractmethod
from typing import TypedDict
from typing_extensions import NotRequired

class Word(TypedDict):
  word: str
  note: NotRequired[str]

class AbstractDictionary(ABC):
  @staticmethod
  @abstractmethod
  def loginCheckCallbackFn(cookie: dict, content: str):
    pass

  @abstractmethod
  def checkCookie(self, cookie: dict):
    pass

  @abstractmethod
  def getGroups(self) -> [(str, int)]:
    pass

  @abstractmethod
  def getTotalPage(self, groupName: str, groupId: int) -> int:
    pass

  @abstractmethod
  def getWordsByPage(self, pageNo: int, groupName: str, groupId: str) -> list[Word]:
    pass
