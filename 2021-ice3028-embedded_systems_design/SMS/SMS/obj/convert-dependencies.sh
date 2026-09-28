#!/bin/sh
# AUTO-GENERATED FILE, DO NOT EDIT!
if [ -f $1.org ]; then
  sed -e 's!^C:/AndroXStudio/legacy/cygwin/lib!/usr/lib!ig;s! C:/AndroXStudio/legacy/cygwin/lib! /usr/lib!ig;s!^C:/AndroXStudio/legacy/cygwin/bin!/usr/bin!ig;s! C:/AndroXStudio/legacy/cygwin/bin! /usr/bin!ig;s!^C:/AndroXStudio/legacy/cygwin/!/!ig;s! C:/AndroXStudio/legacy/cygwin/! /!ig;s!^C:!/cygdrive/c!ig;s! C:! /cygdrive/c!ig;' $1.org > $1 && rm -f $1.org
fi
