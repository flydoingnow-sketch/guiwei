"""Install Guiwei launch agents and Übersicht widgets on macOS."""
from pathlib import Path
import os
import plistlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = Path.home() / 'Library/Application Support/Guiwei'
AGENTS = Path.home() / 'Library/LaunchAgents'
WIDGETS = Path.home() / 'Library/Application Support/Übersicht/widgets'
LABEL = 'local.guiwei.server'
UI_LABEL = 'local.guiwei.ui'

def main():
    if sys.platform != 'darwin':
        sys.exit('归位桌面安装目前仅支持 macOS。')
    if subprocess.run(['/usr/bin/pgrep', '-f', '桌面工作台/server.py'], capture_output=True).returncode == 0:
        sys.exit('检测到旧版工作台正在运行。请先导出任务备份并停用旧版，再安装，避免端口冲突。')
    for directory in (DATA, AGENTS, WIDGETS):
        directory.mkdir(parents=True, exist_ok=True)
    target = f'gui/{os.getuid()}'
    configs = {
        LABEL: {'Label': LABEL, 'ProgramArguments': [sys.executable, str(ROOT / 'server.py')],
                'WorkingDirectory': str(ROOT), 'RunAtLoad': True, 'KeepAlive': True,
                'ThrottleInterval': 10, 'StandardOutPath': str(DATA / 'server.log'),
                'StandardErrorPath': str(DATA / 'error.log')},
        UI_LABEL: {'Label': UI_LABEL, 'ProgramArguments': ['/usr/bin/open', '-b', 'tracesOf.Uebersicht'], 'RunAtLoad': True},
    }
    for label, config in configs.items():
        path = AGENTS / f'{label}.plist'
        subprocess.run(['/bin/launchctl', 'bootout', f'{target}/{label}'], capture_output=True)
        path.write_bytes(plistlib.dumps(config))
        subprocess.run(['/bin/launchctl', 'bootstrap', target, str(path)], check=True)
    for source in (ROOT / 'widgets').glob('*.jsx'):
        destination = WIDGETS / f'guiwei-{source.name}'
        shutil.copy2(source, destination)
    subprocess.run(['/usr/bin/open', '-b', 'tracesOf.Uebersicht'], check=True)
    print('归位已安装。任务数据：', DATA)
    print('请保持项目目录位置不变；移动后重新运行安装脚本。')

if __name__ == '__main__':
    main()
