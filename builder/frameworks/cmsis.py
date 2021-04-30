# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
CMSIS

The ARM Cortex Microcontroller Software Interface Standard (CMSIS) is a
vendor-independent hardware abstraction layer for the Cortex-M processor
series and specifies debugger interfaces. The CMSIS enables consistent and
simple software interfaces to the processor for interface peripherals,
real-time operating systems, and middleware. It simplifies software
re-use, reducing the learning curve for new microcontroller developers
and cutting the time-to-market for devices.

http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php
"""

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
