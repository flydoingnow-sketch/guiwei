"""Remove only Guiwei launch agents and widgets; retain user data."""
from pathlib import Path
import os
import subprocess
import sys
if sys.platform != 'darwin':
    sys.exit('仅支持 macOS。')
for label in ('local.guiwei.server', 'local.guiwei.ui'):
    subprocess.run(['/bin/launchctl', 'bootout', f'gui/{os.getuid()}/{label}'], capture_output=True)
    (Path.home() / 'Library/LaunchAgents' / f'{label}.plist').unlink(missing_ok=True)
for name in ('desktop-workspace.jsx', 'desktop-labels.jsx'):
    (Path.home() / 'Library/Application Support/Übersicht/widgets' / f'guiwei-{name}').unlink(missing_ok=True)
print('已卸载后台与组件。任务数据仍保存在 ~/Library/Application Support/Guiwei。')
