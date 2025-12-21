"""
Quick script to check Resend package structure and correct import
"""
import sys

print("Python version:", sys.version)
print("Python path:", sys.path[:3])

try:
    import resend
    print("\n✓ resend module imported successfully")
    print("resend module location:", resend.__file__)
    print("resend module contents:", dir(resend))
    
    # Try different ways to access Resend
    if hasattr(resend, 'Resend'):
        print("\n✓ resend.Resend found")
        Resend = resend.Resend
        print("Resend class:", Resend)
    else:
        print("\n✗ resend.Resend NOT found")
        
    # Check for alternative locations
    if hasattr(resend, '__all__'):
        print("resend.__all__:", resend.__all__)
        
    # Try importing from submodules
    try:
        from resend.client import Resend as ClientResend
        print("\n✓ Found Resend in resend.client")
    except ImportError as e:
        print(f"\n✗ resend.client.Resend not found: {e}")
        
    try:
        from resend.resend import Resend as ResendResend
        print("\n✓ Found Resend in resend.resend")
    except ImportError as e:
        print(f"\n✗ resend.resend.Resend not found: {e}")
        
except ImportError as e:
    print(f"\n✗ Failed to import resend: {e}")

