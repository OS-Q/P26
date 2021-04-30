import glob
import os
import string

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

env.SConscript("_bare.py")

CMSIS_DIR  = platform.get_package_dir("framework-cmsis")
SWM320_DIR = os.path.join(os.path.split(CMSIS_DIR)[0], "framework-cmsis-swm320")


#
# Allow using custom linker scripts
#

if not board.get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=os.path.join(SWM320_DIR, "swm320.ld"))

#
# Prepare build environment
#

# The final firmware is linked against standard library with two specifications:
# nano.specs - link against a reduced-size variant of libc
# nosys.specs - link against stubbed standard syscalls

env.Append(
    CPPPATH=[
        os.path.join(SWM320_DIR, "CMSIS", "CoreSupport"),
        os.path.join(SWM320_DIR, "CMSIS", "DeviceSupport"),
        os.path.join(SWM320_DIR, "SWM320_StdPeriph_Driver")
    ],

    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs"
    ]
)

#
# Compile CMSIS sources
#

env.BuildSources(
    os.path.join("$BUILD_DIR", "CMSIS"), os.path.join(SWM320_DIR, "CMSIS", "DeviceSupport"),
    src_filter=[
        "-<*>",
        "+<system_SWM320.c>",
        "+<startup/gcc/startup_SWM320.s>"]
)

env.BuildSources(
    os.path.join("$BUILD_DIR", "StdPD"), os.path.join(SWM320_DIR, "SWM320_StdPeriph_Driver"),
    src_filter=[
        "+<*.c>"]
)
