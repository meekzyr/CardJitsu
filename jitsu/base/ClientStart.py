from panda3d.core import *

loadPrcFileData('', 'default-model-extension .bam')

from direct.directnotify.DirectNotifyGlobal import directNotify
import builtins

builtins.directNotify = directNotify
builtins.process = 'client'

from direct.showbase.ShowBase import ShowBase
base = ShowBase()

# The VirtualFileSystem, which has already initialized, doesn't see the mount
# directives in the config(s) yet. We have to force it to load those manually:
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
print(mounts)
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
