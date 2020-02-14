from setuptools import setup
import os
import sys

sys.path += '../'

win64_build = sys.maxsize > 2**32

if sys.platform == 'win32':
    platform_dependencies = ['kernel32.dll', 'user32.dll', 'wsock32.dll', 'ws2_32.dll', 'advapi32.dll', 'opengl32.dll',
                             'glu32.dll', 'gdi32.dll', 'shell32.dll', 'ntdll.dll', 'ws2help.dll', 'rpcrt4.dll',
                             'imm32.dll', 'ddraw.dll', 'shlwapi.dll', 'secur32.dll', 'dciman32.dll', 'comdlg32.dll',
                             'comctl32.dll', 'ole32.dll', 'oleaut32.dll', 'gdiplus.dll', 'winmm.dll', 'iphlpapi.dll',
                             'msvcrt.dll', 'kernelbase.dll', 'msimg32.dll', 'msacm32.dll', 'msvcp140.dll',
                             'setupapi.dll', 'vcruntime140.dll', 'version.dll']
    if win64_build:
        requirements_file = 'packager/requirements.txt'
        distribution = 'win_amd64'
    else:
        requirements_file = 'packager/requirements_win32.txt'
        distribution = 'win32'
else:
    platform_dependencies = ['/usr/lib/libstdc++.*.dylib', '/usr/lib/libz.*.dylib', '/usr/lib/libobjc.*.dylib',
                             '/usr/lib/libSystem.*.dylib', '/usr/lib/libbz2.*.dylib', '/usr/lib/libedit.*.dylib',
                             '/System/Library/**', ]
    requirements_file = 'packager/requirements_darwin.txt'
    distribution = 'macosx_10_9_x86_64'


def build_resources():
    print('Building resources..')
    unbuilt_phases = []
    for file in os.listdir('resources/'):
        if 'phase_' in file:
            if not file.endswith('.mf'):
                unbuilt_phases.append(f'{file}')
            else:
                print(f'Found existing multifile {file}, removing..')
                os.remove(f'resources/{file}')

    for unbuilt_phase in unbuilt_phases:
        print(f'Packaging {unbuilt_phase}..')
        os.system(f'multify -c -f resources/{unbuilt_phase}.mf resources/{unbuilt_phase}')


def cleanup_resources():
    print('Cleaning up resources..')
    for file in os.listdir('resources/'):
        if 'phase_' in file and file.endswith('.mf'):
            os.remove(f'resources/{file}')


def build_game():
    setup(
        name="jitsu",
        options={
            'build_apps': {
                'requirements_path': requirements_file,
                'include_patterns': [
                    'etc/jitsu.dc',
                    'resources/*.mf',
                    'resources/*.ico'
                ],
                'gui_apps': {
                    'jitsu': 'jitsu/base/ClientStart.py',
                },
                'platforms': [
                    distribution,
                ],
                'plugins': [
                    'pandagl',
                    'p3openal_audio',
                ],
                'include_modules': {
                    '*': ['jitsu.account.Account', 'jitsu.objects.TimeManager', 'jitsu.objects.AuthManager',
                          'jitsu.objects.DistributedDistrict', 'jitsu.jitsu.DistributedCardJitsu',
                          'jitsu.jitsu.DistributedSenseiBattle']},
                'exclude_dependencies': platform_dependencies,
                'log_filename': 'jitsu.log',
                'use_optimized_wheels': False,
                'default_prc_dir': 'etc/',
                'build_base': 'packager',
                'extra_prc_files': ['etc/Configrc.prc'],
                'pypi_extra_indexes': [],
            }
        },
    )


if __name__ == '__main__':
    build_resources()
    build_game()
    cleanup_resources()
    print('Done.')
