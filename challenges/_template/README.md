# %challenge-name%

**Author:** %author%

**Difficulty:** %difficulty%

<!-- Baby/Trivial/Easy/Normal/Medium/Hard/Expert/Insane -->

**Category:** %category%

<!-- Misc/Crypto/Pwn/Web/Reverse/Blockchain/Forensics/Mobile/PPC/Pentest/OSINT -->

**Flag:** `%flag or flag template%`

<!-- NOTE: Read https://docs.ctf.gzti.me/zh/guide/dynamic-flag for Flag -->
<!-- NOTE: **Author** can be multiple, separated by `,` -->
<!-- NOTE: Replace %difficulty%, %category%, %author% with the actual value -->

## Description

%description%

## Deployment

<!-- NOTE:

All build files should be in the ./build/src folder

Only 4 files are allowed to be in the root of the ./build folder:

- Dockerfile (required for a container challenge)
- custom.yml (optional, to customize the workflow)
- pre-build.sh (optional, to run before building the challenge)
- post-build.sh (optional, to run after building the challenge)

And you can add files starting with `.git` to your challenge folder.

In which you can config gitattributes, gitignore, etc.

-->

| Port   | CPU(0.1c) | Memory(1M) | Disk(1M) |
| ------ | --------- | ---------- | -------- |
| %port% | %cpu%     | %memory%   | %disk%   |

## Solution

%solution%
