import zipfile
import os
import shutil
import tempfile
from tkinter import Tk, filedialog, simpledialog, messagebox

def patch_bytes(file_path, replacement_map):
    with open(file_path, 'rb') as f:
        data = f.read()
    modified = False
    for original, replacement in replacement_map.items():
        orig_bytes = original.encode()
        if orig_bytes in data:
            padded = replacement.ljust(len(original), '\x00').encode()
            data = data.replace(orig_bytes, padded)
            modified = True
    if modified:
        with open(file_path, 'wb') as f:
            f.write(data)

def main():
    Tk().withdraw()

    ipa_path = filedialog.askopenfilename(
        title="Select .ipa file",
        filetypes=[("IPA Files", "*.ipa")]
    )
    if not ipa_path:
        return

    roblox_host = simpledialog.askstring("roblox.com", "Enter new host for roblox.com (exactly 10 characters):")
    if not roblox_host or len(roblox_host) != 10:
        messagebox.showerror("Error", "roblox.com address must be exactly 10 characters long.")
        return

    rbxcdn_host = simpledialog.askstring("rbxcdn.com", "Enter new host for rbxcdn.com (exactly 10 characters):")
    if not rbxcdn_host or len(rbxcdn_host) != 10:
        messagebox.showerror("Error", "rbxcdn.com address must be exactly 10 characters long.")
        return

    domains = {
        "roblox.com": roblox_host,
        "rbxcdn.com": rbxcdn_host
    }

    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(ipa_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    payload_path = os.path.join(temp_dir, "Payload")
    app_dir = next((os.path.join(payload_path, d) for d in os.listdir(payload_path) if d.endswith(".app")), None)
    if not app_dir:
        messagebox.showerror("Error", ".app folder not found in Payload.")
        return

    # Patch Roblox binary
    binary_path = os.path.join(app_dir, "Roblox")
    if os.path.isfile(binary_path):
        patch_bytes(binary_path, domains)

    # Patch Info.plist
    plist_path = os.path.join(app_dir, "Info.plist")
    if os.path.isfile(plist_path):
        patch_bytes(plist_path, domains)

    # Patch RobloxLib framework
    robloxlib_path = os.path.join(app_dir, "Frameworks", "RobloxLib.framework", "RobloxLib")
    if os.path.isfile(robloxlib_path):
        patch_bytes(robloxlib_path, domains)

    # Create patched .ipa
    patched_ipa = ipa_path.replace(".ipa", "_patched.ipa")
    with zipfile.ZipFile(patched_ipa, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                zipf.write(full_path, rel_path)

    shutil.rmtree(temp_dir)
    messagebox.showinfo("Done", f"Patching completed!\nFile saved as:\n{patched_ipa}")

if __name__ == "__main__":
    main()