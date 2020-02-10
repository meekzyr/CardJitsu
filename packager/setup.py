from setuptools import setup
import sys

sys.path += '../'

windows_dependencies = ['kernel32.dll', 'user32.dll', 'wsock32.dll', 'ws2_32.dll',
                        'advapi32.dll', 'opengl32.dll', 'glu32.dll', 'gdi32.dll',
                        'shell32.dll', 'ntdll.dll', 'ws2help.dll', 'rpcrt4.dll',
                        'imm32.dll', 'ddraw.dll', 'shlwapi.dll', 'secur32.dll',
                        'dciman32.dll', 'comdlg32.dll', 'comctl32.dll', 'ole32.dll',
                        'oleaut32.dll', 'gdiplus.dll', 'winmm.dll', 'iphlpapi.dll', 'msvcrt.dll',
                        'kernelbase.dll', 'msimg32.dll', 'msacm32.dll', 'msvcp140.dll', 'setupapi.dll',
                        'vcruntime140.dll', 'version.dll']
setup(
    name="jitsu",
    options={
        'build_apps': {
            'requirements_path': 'packager/requirements.txt',
            'include_patterns': [
                'etc/jitsu.dc',
                'resources/**/*.rgb',
                'resources/**/*.png',
                'resources/**/*.bam',
                'resources/**/*.jpg',
                'resources/**/*.ttf',
                'resources/*.ico'
            ],
            'gui_apps': {
                'jitsu': 'jitsu/base/ClientStart.py',
            },
            'platforms': [
                'win_amd64',
            ],
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
            'include_modules': {
                '*': ['jitsu.account.Account', 'jitsu.objects.TimeManager', 'jitsu.objects.AuthManager',
                      'jitsu.objects.DistributedDistrict', 'jitsu.jitsu.DistributedCardJitsu']},
            'exclude_dependencies': windows_dependencies,
            'log_filename': '_logfile.log',
            'use_optimized_wheels': False,
            'default_prc_dir': 'etc/',
            'build_base': 'packager',
            'extra_prc_files': ['etc/general.prc'],
            'pypi_extra_indexes': [],
        }
    },
)
