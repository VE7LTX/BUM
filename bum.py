import shutil
import os
import psutil

def get_drive_space():
    """
    Retrieves the available drives and their used and free space, along with file system type and label.
    
    Returns:
        list of tuples: Each tuple contains (drive, total space, used space, free space, file system type, label) in bytes.
    """
    drives = []
    # On Windows, check each drive letter
    if os.name == 'nt':
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = f"{drive}:\\"
            if os.path.exists(drive_path):
                total, used, free = shutil.disk_usage(drive_path)
                file_system_type = psutil.disk_partitions()
                for part in file_system_type:
                    if part.mountpoint == drive_path:
                        fs_type = part.fstype
                        label = part.device if part.device else "No Label"
                        break
                drives.append((drive_path, total, used, free, fs_type, label))
    # On Unix-like systems, check mounted drives
    else:
        for part in psutil.disk_partitions():
            if os.path.exists(part.mountpoint):
                total, used, free = shutil.disk_usage(part.mountpoint)
                label = part.device if part.device else "No Label"
                drives.append((part.mountpoint, total, used, free, part.fstype, label))
    return drives

def display_drives():
    """
    Displays the available drives and their storage details including file system type and label.
    """
    drives = get_drive_space()
    for index, (drive, total, used, free, fs_type, label) in enumerate(drives):
        print(f"{index + 1}. Drive: {drive} (File System: {fs_type}, Label: {label})")
        print(f"   Total Space: {total / (1024**3):.2f} GB")
        print(f"   Used Space: {used / (1024**3):.2f} GB")
        print(f"   Free Space: {free / (1024**3):.2f} GB")
        print("-" * 40)
    return drives

def select_drive(drives):
    """
    Allows the user to select a drive from a list by entering a number.
    
    Args:
        drives (list): List of drives obtained from get_drive_space().
    
    Returns:
        str: The selected drive path.
    """
    while True:
        try:
            choice = int(input("Enter the number of the drive: ")) - 1
            if 0 <= choice < len(drives):
                return drives[choice][0]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def confirm_destination():
    """
    Confirms the destination drive by asking the user to confirm twice.
    
    Returns:
        bool: True if confirmed twice, False otherwise.
    """
    confirm1 = input("Please confirm the destination drive by typing 'yes': ").lower() == 'yes'
    confirm2 = input("Please confirm again by typing 'yes': ").lower() == 'yes'
    return confirm1 and confirm2

def copy_to_drive():
    """
    Facilitates the copying of files from a source drive to a destination drive selected by the user.
    Ensures that the source and destination are not the same and confirms the destination before proceeding.
    """
    common_exclusions = ['\\Windows\\', '\\Program Files\\', '\\Program Files (x86)\\', '\\ProgramData\\']
    print("Do you want to exclude common directories and file types? (yes/no)")
    exclude_common = input().lower() == 'yes'
    if exclude_common:
        print("Please confirm if you really want to exclude common directories and file types (yes/no)")
        confirm_exclude = input().lower() == 'yes'
        exclude_patterns = common_exclusions.copy() if confirm_exclude else []
    else:
        exclude_patterns = []

    if confirm_exclude:
        print("Common directories to exclude:")
        for exclusion in common_exclusions:
            print(f"- {exclusion}")

    print("\nEnter custom file extensions to include (e.g., '.txt'). Enter blank twice to continue.")
    consecutive_blanks = 0
    while consecutive_blanks < 2:
        ext = input("File extension to include: ")
        if ext.strip() == "":
            consecutive_blanks += 1
        else:
            consecutive_blanks = 0
            if ext not in exclude_patterns:
                exclude_patterns.remove(ext)
        print("Current inclusions:", [ext for ext in common_exclusions if ext not in exclude_patterns])

    while True:
        print("Available Drives:")
        drives = display_drives()
        print("\nSelect the source drive:")
        source = select_drive(drives)
        print("\nSelect the destination drive:")
        destination = select_drive(drives)
        
        if source == destination:
            print("Source and destination drives cannot be the same. Restarting the process.")
            continue
        
        source_total, source_used, source_free = shutil.disk_usage(source)
        dest_total, dest_used, dest_free = shutil.disk_usage(destination)
        
        if source_used > dest_free:
            print("Not enough space on the destination drive. Restarting the process.")
            continue
        
        if not confirm_destination():
            print("Destination drive confirmation failed. Restarting the process.")
            continue
        
        try:
            for root, dirs, files in os.walk(source):
                if any(excl in root for excl in exclude_patterns):
                    continue
                for file in files:
                    if any(file.endswith(ext) for ext in exclude_patterns if ext.startswith('.')):
                        continue
                    src_path = os.path.join(root, file)
                    dest_path = src_path.replace(source, destination, 1)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied {src_path} to {dest_path}")
            break
        except Exception as e:
            print(f"Error during copying: {e}. Restarting the process.")
            continue

# Example usage
copy_to_drive()
