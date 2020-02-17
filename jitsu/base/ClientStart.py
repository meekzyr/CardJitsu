from panda3d.core import *
import sys
from direct.directnotify.DirectNotifyGlobal import directNotify
import builtins

builtins.directNotify = directNotify
builtins.process = 'client'

loadPrcFileData('', 'default-model-extension .bam')

if len(sys.argv) > 1 and sys.argv[1] == '--dev':
    loadPrcFile('etc/Configrc.prc')
else:
    vfs = VirtualFileSystem.getGlobalPtr()
    mounts = ConfigVariableList('vfs-mount')
    for mount in mounts:
        mountFile, mountPoint = (mount.split(' ', 2) + [None, None, None])[:2]
        mountFile = Filename(mountFile)
        mountFile.makeAbsolute()
        mountPoint = Filename(mountPoint)
        vfs.mount(mountFile, mountPoint, 0)

from direct.showbase.ShowBase import ShowBase
base = ShowBase()
base.disableMouse()

from jitsu.base.Options import Options
base.options = builtins.options = Options()


cbMgr = CullBinManager.getGlobalPtr()
cbMgr.addBin('gui-popup', cbMgr.BTUnsorted, 60)

from jitsu.objects import JitsuClientRepository

base.cr = JitsuClientRepository.JitsuClientRepository()
base.run()
