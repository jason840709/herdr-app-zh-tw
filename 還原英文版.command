#!/bin/zsh
cd -- "${0:A:h}" || exit 1
herdr_python="$(command -v python3 2>/dev/null)"
if [[ -z "$herdr_python" ]] || ! "$herdr_python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
  printf '需要 Python 3.9 或更新版本。請先安裝 Python 3，再執行此工具。\n'
  herdr_result=1
else
  "$herdr_python" -B './中文化工具.py' restore
  herdr_result=$?
fi
if [[ -t 0 ]]; then
  printf '\n按 Enter 關閉視窗。'
  read -r herdr_reply
fi
exit "$herdr_result"
