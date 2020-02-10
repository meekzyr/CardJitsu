from panda3d.core import *
import sys
from direct.directnotify.DirectNotifyGlobal import directNotify
import builtins

builtins.directNotify = directNotify
builtins.process = 'client'

loadPrcFileData('', 'default-model-extension .bam')

want_dev = False
if len(sys.argv) > 1 and sys.argv[1] == '--dev':
    want_dev = True
    loadPrcFile('etc/Configrc.prc')

builtins.want_dev = want_dev

from direct.showbase.ShowBase import ShowBase
base = ShowBase()

if not want_dev:
    vfs = VirtualFileSystem.getGlobalPtr()
    mounts = ConfigVariableList('vfs-mount')
    for mount in mounts:
        mountFile, mountPoint = (mount.split(' ', 2) + [None, None, None])[:2]
        mountFile = Filename(mountFile)
        mountFile.makeAbsolute()
        mountPoint = Filename(mountPoint)
        vfs.mount(mountFile, mountPoint, 0)

base.disableMouse()

cbMgr = CullBinManager.getGlobalPtr()
cbMgr.addBin('gui-popup', cbMgr.BTUnsorted, 60)

from jitsu.objects import JitsuClientRepository

base.cr = JitsuClientRepository.JitsuClientRepository()
base.cr.startConnect()
base.run()
