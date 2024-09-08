from abc import ABC, abstractmethod

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
  def getWordsByPage(self, pageNo: int, groupName: str, groupId: str) -> [str]:
    pass
