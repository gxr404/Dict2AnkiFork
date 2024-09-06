from .constants import MODEL_FIELDS, BASIC_OPTION, EXTRA_OPTION
import logging

logger = logging.getLogger('dict2Anki.noteManager')
try:
    from aqt import mw
    import anki
except ImportError:
    from test.dummy_aqt import mw
    from test import dummy_anki as anki


def getDeckList():
    return [deck['name'] for deck in mw.col.decks.all()]


def getWordsByDeck(deckName) -> [str]:
    notes = mw.col.findNotes(f'deck:"{deckName}"')
    words = []
    for nid in notes:
        note = mw.col.getNote(nid)
        if note.model().get('name', '').lower().startswith('dict2anki') and note['term']:
            words.append(note['term'])
    return words


def getNotes(wordList, deckName) -> list:
    notes = []
    for word in wordList:
        note = mw.col.findNotes(f'deck:"{deckName}" term:"{word}"')
        if note:
            notes.append(note[0])
    return notes


def getOrCreateDeck(deckName, model):
    deck_id = mw.col.decks.id(deckName)
    deck = mw.col.decks.get(deck_id)
    mw.col.decks.select(deck['id'])
    mw.col.decks.save(deck)
    mw.col.models.setCurrent(model)
    model['did'] = deck['id']
    mw.col.models.save(model)
    mw.col.reset()
    mw.reset()
    return deck


def getOrCreateModel(modelName):
    model = mw.col.models.byName(modelName)
    if model:
        if set([f['name'] for f in model['flds']]) == set(MODEL_FIELDS):
            return model
        else:
            logger.warning('模版字段异常，自动删除重建')
            mw.col.models.rem(model)

    logger.info(f'创建新模版:{modelName}')
    newModel = mw.col.models.new(modelName)
    for field in MODEL_FIELDS:
        mw.col.models.addField(newModel, mw.col.models.newField(field))
    return newModel


def getOrCreateModelCardTemplate(modelObject, cardTemplateName):
    logger.info(f'添加卡片类型:{cardTemplateName}')
    existingCardTemplate = modelObject['tmpls']
    if cardTemplateName in [t.get('name') for t in existingCardTemplate]:
        return
    cardTemplate = mw.col.models.newTemplate(cardTemplateName)
    # 卡片正面
    cardTemplate['qfmt'] = '''
        <table>
            <tr>
                <td>
                    <h1 class="term">{{term}}</h1><br>
                    <div> 英 [{{BrEPhonetic}}] 美 [{{AmEPhonetic}}]</div>
                </td>
                <td><img {{image}} height="120px"></td>
            </tr>
        </table>
        {{BrEPron}}
        {{AmEPron}}
        <hr>
        <dl class="definition">
            <dt>释义：</dt>
            <dd>Tap to View</dd>
        </dl>
        <hr>
        <dl class="dl">
            <dt>短语：</dt>
            <dd><table>{{phraseFront}}</table></dd>
        </dl>
        <hr>
        <dl class="dl">
            <dt>例句：</dt>
            <dd><table>{{sentenceFront}}</table></dd>
        </dl>
    '''
    # 卡片背面
    cardTemplate['afmt'] = '''
        <table>
            <tr>
                <td>
                    <h1 class="term">{{term}}</h1><br>
                    <div> 英 [{{BrEPhonetic}}] 美 [{{AmEPhonetic}}]</div>
                </td>
                <td><img {{image}} height="120px"></td>
            </tr>
        </table>
        {{BrEPron}}
        {{AmEPron}}
        <hr>
        <dl class="definition">
            <dt>释义：</dt>
            {{definition}}
        </dl>
        <hr>
        <dl class="dl">
            <dt>短语：</dt>
            <dd><table>{{phraseBack}}</table></dd>
        </dl>
        <hr>
        <dl class="dl">
            <dt>例句：</dt>
            <dd><table>{{sentenceBack}}</table></dd>
        </dl>
    '''
    modelObject['css'] = '''
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: left;
            color: black;
            background-color: white;
        }
        .term {
            font-size : 35px;
        }
        .definition {
            font-size :14px;
        }
        .definition dd {
            margin: 10px 0 10px 20px;
        }
        .definition dt {
            font-weight: bold;
        }
        .dl {
            font-size: 14px;
        }
        .dl dd{
            margin-left: 20px;
        }
        .dl dt {
            font-weight: bold;
        }
    '''
    mw.col.models.addTemplate(modelObject, cardTemplate)
    mw.col.models.add(modelObject)


def addNoteToDeck(deckObject, modelObject, currentConfig: dict, oneQueryResult: dict):
    if not oneQueryResult:
        logger.warning(f'查询结果{oneQueryResult} 异常，忽略')
        return
    modelObject['did'] = deckObject['id']

    newNote = anki.notes.Note(mw.col, modelObject)
    newNote['term'] = oneQueryResult['term']
    for configName in BASIC_OPTION + EXTRA_OPTION:
        logger.debug(f'字段:{configName}--结果:{oneQueryResult.get(configName)}')
        if oneQueryResult.get(configName):
            # 短语例句
            if configName in ['sentence', 'phrase'] and currentConfig[configName]:
                newNote[f'{configName}Front'] = '\n'.join(
                    [f'<tr><td>{e.strip()}</td></tr>' for e, _ in oneQueryResult[configName]])
                newNote[f'{configName}Back'] = '\n'.join(
                    [f'<tr><td>{e.strip()}</td><td>{c.strip()}</td></tr>' for e, c in oneQueryResult[configName]])
            # 图片
            elif configName == 'image':
                newNote[configName] = f'src="{oneQueryResult[configName]}"'
            # 释义
            elif configName == 'definition' and currentConfig[configName]:
                newNote[configName] = '\n'.join([f'<dd>{item.strip()}</dd>' for item in oneQueryResult[configName]])
            # 发音
            elif configName in EXTRA_OPTION[:2]:
                newNote[configName] = f"[sound:{configName}_{oneQueryResult['term']}.mp3]"
            # 其他
            elif currentConfig[configName]:
                newNote[configName] = oneQueryResult[configName]

    mw.col.addNote(newNote)
    mw.col.reset()
    logger.info(f"添加笔记{newNote['term']}")
