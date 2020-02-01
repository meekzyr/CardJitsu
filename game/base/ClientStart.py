from panda3d.core import *

loadPrcFile("config/Config.prc")

from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify
__builtins__.process = 'client'

from direct.showbase.ShowBase import ShowBase
base = ShowBase()

# The VirtualFileSystem, which has already initialized, doesn't see the mount
# directives in the config(s) yet. We have to force it to load those manually:
vfs = VirtualFileSystem.getGlobalPtr()
mounts = ConfigVariableList('vfs-mount')
for mount in mounts:
    mountfile, mountpoint = (mount.split(' ', 2) + [None, None, None])[:2]
    vfs.mount(Filename(mountfile), Filename(mountpoint), 0)

base.disableMouse()


from direct.gui import DirectGuiGlobals
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))

cbMgr = CullBinManager.getGlobalPtr()
cbMgr.addBin('gui-popup', cbMgr.BTUnsorted, 60)

from game.objects import JitsuClientRepository

base.cr = JitsuClientRepository.JitsuClientRepository()
base.cr.startConnect()
base.run()
