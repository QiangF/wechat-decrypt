import gdb
import re
import sys
sys.stdout = sys.stderr
# relative = "0x658FC90" # linux_4.1.0.10
relative = "0x6586C90" # linux_4.1.0.11

base = next(line.split()[0] for line in gdb.execute("info proc mapping", to_string=True).splitlines() if line.strip().endswith("/wechat"))
bp = gdb.Breakpoint(f"* {base} + {relative}")
print(f"base = {base}, relative = {relative}, breakpoint has been set, please login wechat")
gdb.execute("continue") # wait to breakpoint
print(f"breakpoint hit_count = {bp.hit_count}, now, reading memory")
assert gdb.execute("x/1gx $rsi+16", to_string=True).strip().endswith('0x0000000000000020'), "expect size == 0x20 == 32 bytes"
key = re.compile(r"^.*?:\s*|0x|\s+", re.MULTILINE).sub("", gdb.execute("x/32bx *(void**)($rsi+8)", to_string=True))
print(f"key = {key}")

# windows may use https://github.com/ssbssa/gdb/releases/download/gdb-16.3.90.20250511/gdb-16.3.90.20250511-x86_64-python.7z

# 1. 启动微信（若已登录需退出登录）
# 2. 执行命令
# sudo gdb --pid=$(pgrep wechat$) --batch-silent --command=/usr/local/bin/wechat/wechat_gdb.py
# 3. 登录微信，得到 key
