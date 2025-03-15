import os
from zipfile import ZipFile
from addon.constants import MODEL_NAME


def create_zip():
    file_paths = []
    exclude_dirs = ['test', '__pycache__', '.git', '.idea', '.pytest_cache', 'screenshots', 'venv', '.vscode',]
    exclude_files = [
        'README.md', '.gitignore', '.travis.yml', 'deploy.py', 'requirements.txt', '.DS_Store',
        'meta.json',  'OLD_README.md', 'pkg.py']
    exclude_ext = ['.png', '.ui', '.qrc', '.log', '.zip', '.tpl']
    for dirname, sub_dirs, files in os.walk("."):
        for d in exclude_dirs:
            if d in sub_dirs:
                sub_dirs.remove(d)
        for f in exclude_files:
            if f in files:
                files.remove(f)
        for ext in exclude_ext:
            for f in files[:]:
                if f.endswith(ext):
                    files.remove(f)
        for filename in files:
            file_paths.append(os.path.join(dirname, filename))

    with ZipFile(f'{MODEL_NAME}.zip', 'w') as zf:
        for file in file_paths:
            zf.write(file)

def main():
    create_zip()
    # with open('anki_addon_page.tpl', encoding='utf-8') as tpl:
    #     return update('Dict2Anki（有道,欧陆词典单词本同步工具）', '有道 欧陆 导入 同步', tpl.read())


if __name__ == '__main__':
    main()
