#!/usr/bin/env python3
"""Patch getm_fabm.F90 to pass dt to init_gotm_fabm, so temporal_mean variables work."""

FILE_PATH = r"C:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src\3d\getm_fabm.F90"

def main():
    with open(FILE_PATH, 'r') as f:
        content = f.read()
    
    # We need to add dt to the init_gotm_fabm call
    # First, make sure variables_3d dt is accessible
    # It's already imported via "use variables_3d"
    
    # Patch 1: the call inside _NEW_GOTM_ section (line 188)
    old_call1 = "   call init_gotm_fabm(kmax)\n#else\n   call init_gotm_fabm(kmax,NAMLST2,'gotm_fabm.nml')"
    new_call1 = "   call init_gotm_fabm(kmax, dt)\n#else\n   call init_gotm_fabm(kmax,NAMLST2,'gotm_fabm.nml')"
    
    if old_call1 in content:
        content = content.replace(old_call1, new_call1)
        print("Patched: init_gotm_fabm(kmax) -> init_gotm_fabm(kmax, dt)")
    else:
        print("WARNING: Could not find pattern for patch 1")
        # Try to find the line
        import re
        m = re.search(r'call init_gotm_fabm\(kmax\)', content)
        if m:
            print(f"Found at position {m.start()}: {m.group()}")
            # Show context
            start = max(0, m.start() - 50)
            end = min(len(content), m.end() + 50)
            print(f"Context: {content[start:end]}")
    
    # Save
    with open(FILE_PATH, 'w') as f:
        f.write(content)
    
    print("\nDone. Now you need to recompile GETM.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
