import os
import logging
from addon.queryApi.cambridge import API
import pytest

logger = logging.getLogger(__name__)
api = API()

keys = ('term', 'definition', 'phrase', 'image', 'sentence', 'BrEPhonetic', 'AmEPhonetic', 'BrEPron', 'AmEPron')

def get_missing_filed_set(res):
  ret = []
  for key in keys:
    if not res.get(key):
      ret.append(key)
  return set(ret)


def test_eudict_no_phrase_and_image():
  res = api.query('about')
  ret = get_missing_filed_set(res)
  expect = {'image','phrase', 'sentence'}
  assert ret == expect
