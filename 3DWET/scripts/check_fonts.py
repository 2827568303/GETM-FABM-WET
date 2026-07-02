"""Check and configure Chinese font for matplotlib."""
import matplotlib.font_manager as fm
import matplotlib
import os

# Reload font manager
fm._load_fontmanager(try_read_cache=False)

# Check for Chinese fonts
chinese_fonts = []
for f in fm.fontManager.ttflist:
    if any(name in f.name for name in ['SimHei', 'SimSun', 'Microsoft YaHei', 'WenQuanYi', 'WQY']):
        chinese_fonts.append((f.name, f.fname))
        print(f"Found: {f.name} -> {f.fname}")

if not chinese_fonts:
    # Try to add from ~/.fonts
    font_dir = os.path.expanduser('~/.fonts')
    if os.path.exists(font_dir):
        for fname in os.listdir(font_dir):
            if fname.endswith(('.ttf', '.ttc')):
                fpath = os.path.join(font_dir, fname)
                try:
                    font = fm.FontProperties(fname=fpath)
                    fm.fontManager.addfont(fpath)
                    print(f"Added: {fname}")
                except Exception as e:
                    print(f"Failed to add {fname}: {e}")

    # Reload
    fm._load_fontmanager(try_read_cache=False)
    for f in fm.fontManager.ttflist:
        if any(name in f.name for name in ['SimHei', 'SimSun', 'Microsoft YaHei', 'WenQuanYi', 'WQY']):
            chinese_fonts.append((f.name, f.fname))
            print(f"Found after reload: {f.name} -> {f.fname}")

print(f"\nTotal Chinese fonts found: {len(chinese_fonts)}")
if chinese_fonts:
    print(f"Will use: {chinese_fonts[0][0]}")
