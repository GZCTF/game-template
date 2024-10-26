#!/bin/bash

set -euo pipefail

# This script is executed BEFORE the build process of the challenge.
# You can use this script to install dependencies, build the binary, etc.
# ** This script is executed in the challenge directory. **
# ** Remove this file if you don't need it. **

# You can use the following environment variables:
#   NAME: <YOUR_CHALLENGE_DIR_NAME>
#   CATEGORY: <YOUR_CHALLENGE_CATEGORY_DIR_NAME>
#   REGISTRY: <THE_REGISTRY_WHERE_YOUR_IMAGE_IS_STORED>

# Example:

# gcc -o build/remember_it_0 build/src/remember_it_0.c
# mkdir -p attachments
# cp build/remember_it_0 attachments/remember_it_0
# cp build/src/remember_it_0.c attachments/remember_it_0.c
