#!/bin/bash

set -euo pipefail

# This script is executed AFTER the build process of the challenge.
# You can use this script to copy the built binary to the attachments directory, etc.
# ** This script is executed in the challenge directory. **
# ** Remove this file if you don't need it. **

# You can use the following environment variables:
#   NAME: <YOUR_CHALLENGE_DIR_NAME>
#   CATEGORY: <YOUR_CHALLENGE_CATEGORY_DIR_NAME>
#   REGISTRY: <THE_REGISTRY_WHERE_YOUR_IMAGE_IS_STORED>

# Example:

# temprepository="$(tr [A-Z] [a-z] <<< $REGISTRY/$GITHUB_REPOSITORY/$NAME)"
# mkdir -p attachments
# docker rm tempname || true
# tempid=$(docker create --name tempname $temprepository:latest)
# docker cp $tempid:/home/ctf/macho_parser attachments/
# docker rm tempname
# cp -av build/app attachments/
# cp -av build/main.c attachments/macho_parser.c
