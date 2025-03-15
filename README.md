# Dict2AnkiFork

Fork自原项目[Dict2Anki](https://github.com/megachweng/Dict2Anki), 由于已经不维护了无人修bug


[原README.md](./OLD_README.md)文档


## 改动

- 🛠️ 升级至Qt6，使其能支持最新版的anki
- 💪 添加获取单词源 “百度翻译”
- 💪 添加单词查询和音频下载源 “剑桥词典”
- 💪 添加配置可下载所有发音

## 使用

两种方式:

- 通过[ankiweb](https://ankiweb.net/shared/info/456732182)安装, 插件代码`456732182`

- 直接`git clone`下载到 用户anki插件目录即可

```bash
git clone git@github.com:gxr404/Dict2AnkiFork.git /Users/xxxx/Library/Application\ Support/Anki2/addons21/Dict2AnkiFork
```

## Test

```py
pytest test
```


## Development Guide

Python == 3.12.5

```
export PYTHONPATH='xxx/Dict2Anki'
export DEVDICT2ANKI=1
pip install -r requirements.txt
python __init__.py
```
