import os
import shutil
import uuid

def move_files_unique(src_folder, dst_folder):
    if not os.path.exists(src_folder):
        raise FileNotFoundError(f"Source folder not found: {src_folder}")
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    for filename in os.listdir(src_folder):
        src_path = os.path.join(src_folder, filename)
        if not os.path.isfile(src_path):
            continue

        name, ext = os.path.splitext(filename)
        dst_path = os.path.join(dst_folder, filename)

        while os.path.exists(dst_path):
            unique_suffix = uuid.uuid4().hex[:8]
            dst_path = os.path.join(dst_folder, f"{name}_{unique_suffix}{ext}")

        shutil.move(src_path, dst_path)
        print(f"Moved: {src_path} -> {dst_path}")

def copy_all_images(src_folder, dst_folder):
    if not os.path.exists(src_folder):
        raise FileNotFoundError(f"Source folder not found: {src_folder}")
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    valid_exts = {'.jpg', '.jpeg', '.png'}

    for root, _, files in os.walk(src_folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in valid_exts:
                continue

            src_path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            dst_path = os.path.join(dst_folder, file)

            while os.path.exists(dst_path):
                unique_suffix = uuid.uuid4().hex[:8]
                dst_path = os.path.join(dst_folder, f"{name}_{unique_suffix}{ext}")

            shutil.copy2(src_path, dst_path)
            print(f"Copied: {src_path} -> {dst_path}")

if __name__ == "__main__":
    source = "dataset/old_leafs"
    target = "dataset/leafs"
    # move_files_unique(source, target)
    copy_all_images(source, target)
