import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboard/templates/dashboard/ghi.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function openEmailGetModal' in line or 'function closeEmailGetModal' in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print 5 lines
        for j in range(idx, min(len(lines), idx+6)):
            print(f"  {j+1}: {lines[j].rstrip()}")
