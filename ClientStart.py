from panda3d.core import *
import os
loadPrcFile("config/Config.prc")

# We're using ogg
loadPrcFileData("", "audio-library-name p3openal_audio")
bgmExt = '.ogg'
sfxExt = '.ogg'

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
from direct.directnotify.DirectNotifyGlobal import directNotify

__builtins__.directNotify = directNotify

import JitsuClientRepository
base.cr = JitsuClientRepository.JitsuClientRepository()
base.cr.startConnect()
base.bgmExt = bgmExt
base.sfxExt = base.sfxExt2 = sfxExt

base.run()
