from PIL import Image
import os
import argparse
from pathlib import Path

SUPPORTED_FILE_FORMATS = ('jpg, jpeg, png')

def save_img(img, dest):
    save_dir = os.path.dirname(dest)
    if not os.path.exists(save_dir): os.makedirs(save_dir)
    img.save(dest, optimize=True)


def resize_img_by_min_dimension(img, min_dim):
    
    if min_dim < 0: return

    if img.size[0] < img.size[1]:
        percent = float(min_dim) / img.size[0]
        max_dim = int(img.size[1] * percent)
        img = img.resize((min_dim, max_dim), Image.LANCZOS)
    else:
        percent = float(min_dim) / img.size[1]
        max_dim = int(img.size[0] * percent)
        img = img.resize((max_dim, min_dim), Image.LANCZOS)

    return img


def resize_img_by_max_dimension(img, max_dim):

    if max_dim < 0: return

    if img.size[0] > img.size[1]:
        percent = float(max_dim) / img.size[0]
        min_dim = int(img.size[1] * percent)
        img = img.resize((max_dim, min_dim), Image.Resampling.LANCZOS)
    else:
        percent = float(max_dim) / img.size[1]
        min_dim = int(img.size[0] * percent)
        img = img.resize((min_dim, max_dim), Image.Resampling.LANCZOS)

    return img


def save_img_resized_by_percent(img_path, dest, percent, min_dim=None):

    if percent <= 0 or percent > 1: return

    img = Image.open(img_path)

    h_new = int(img.size[0] * percent)
    w_new = int(img.size[1] * percent)
    
    # min dimension is a strict threshold that resize should respect

    if min_dim is not None and (img.size[0] > min_dim and img.size[1] > min_dim) and (h_new < min_dim or w_new < min_dim):
        img = resize_img_by_min_dimension(img, min_dim)
    else:
        img = img.resize((h_new, w_new), Image.LANCZOS)

    save_img(img, dest)

    print(f'{img_path} -> {dest}')


def save_img_resized_by_min_dimension(img_path, dest, min_dim):
    img = Image.open(img_path)
    img = resize_img_by_min_dimension(min_dim)
    save_img(img, dest)

    print(f'{img_path} -> {dest}')


def save_img_resized_by_max_dimension(img_path, dest, max_dim):
    img = Image.open(img_path)
    img = resize_img_by_max_dimension(img, max_dim)
    save_img(img, dest)

    print(f'{img_path} -> {dest}')


def create_directory_if_not_exists(directory_path):

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def resize_multiple_by_percent(in_path, out_path, percent=0.5, min_dim = None):

    files = os.listdir(in_path)

    if not files: return

    if in_path[-1] != '/': in_path += '/'
    if out_path[-1] != '/': out_path += '/'
    
    create_directory_if_not_exists(out_path)
    
    for fname in files:
        file_format = fname.split('.')[-1]
        if file_format not in SUPPORTED_FILE_FORMATS: continue
        save_img_resized_by_percent(in_path + fname, out_path + fname, percent, min_dim)


def resize_multiple_by_min_dimension(in_path, out_path, min_dim):

    files = os.listdir(in_path)

    if not files: return

    if in_path[-1] != '/': in_path += '/'
    if out_path[-1] != '/': out_path += '/'
    
    create_directory_if_not_exists(out_path)
    
    for fname in files:
        file_format = fname.split('.')[-1]
        if file_format not in SUPPORTED_FILE_FORMATS: continue
        save_img_resized_by_min_dimension(in_path + fname, out_path + fname, min_dim)


def resize_multiple_by_max_dimension(in_path, out_path, max_dim):

    files = os.listdir(in_path)

    if not files: return

    if in_path[-1] != '/': in_path += '/'
    if out_path[-1] != '/': out_path += '/'
    
    create_directory_if_not_exists(out_path)
    
    for fname in files:
        file_format = fname.split('.')[-1]
        if file_format not in SUPPORTED_FILE_FORMATS: continue
        save_img_resized_by_max_dimension(in_path + fname, out_path + fname, max_dim)


def normalize_path(path):
    return str(Path(path)).replace('\\', '/')


def is_file(path):
    return Path(path).is_file()


def is_dir(path):
    return Path(path).is_dir()


def path_exists(path):
    return Path(path).exists()

def resize_by_percent(input_path, output_path, percent, min_dim=None):

    if is_file(input_path):
        save_img_resized_by_percent(input_path, output_path, percent, min_dim)
    elif is_dir(input_path):
        resize_multiple_by_percent(input_path, output_path, percent, min_dim)


def resize_by_min_dimension(input_path, output_path, min_dim):

    if is_file(input_path):
        save_img_resized_by_min_dimension(input_path, output_path, min_dim)
    elif is_dir(input_path):
        resize_multiple_by_min_dimension(input_path, output_path, min_dim)


def resize_by_max_dimension(input_path, output_path, max_dim):

    if is_file(input_path):
        save_img_resized_by_max_dimension(input_path, output_path, max_dim)
    elif is_dir(input_path):
        resize_multiple_by_max_dimension(input_path, output_path, max_dim)


def resize_and_save_based_on_args(args):

    if args.max_dim is not None:

        resize_by_max_dimension(args.input_path, args.output_path, args.max_dim)

    elif args.percent is not None and args.min_dim is not None:
        
        resize_by_percent(args.input_path, args.output_path, args.percent, args.min_dim)

    elif args.percent is not None:

        resize_by_percent(args.input_path, args.output_path, args.percent)

    elif args.min_dim is not None:

        resize_by_min_dimension(args.input_path, args.output_path, args.min_dim)

    else:

        resize_by_percent(args.input_path, args.output_path, 0.5)


def main():
    
    parser = argparse.ArgumentParser(
        description="A script that resizes images individually or in batch."
    )

    parser.add_argument("input_path", type=str, help="Input: path of single image or folder with multiple images")
    parser.add_argument("output_path", type=str, help="Output: path of single image or folder with multiple images")

    parser.add_argument("-p", "--percent", type=float, help="Percentage (from 0 to 1) of original image to resize to (default: 0.5)")
    parser.add_argument("-m", "--min_dim", type=int, help="Minimum dimension of the resized image")
    parser.add_argument("-M", "--max_dim", type=int, help="Maximum dimension of the resized image")

    args = parser.parse_args()

    if args.percent is not None and args.max_dim is not None:
        print("Cannot use --percent (p) with --max_dim (M)")
        exit(1)

    args.input_path = normalize_path(args.input_path)
    args.output_path = normalize_path(args.output_path)

    if not path_exists(args.input_path):
        print(f"Cannot find path: {args.input_path}")
        exit(1)

    resize_and_save_based_on_args(args)


if __name__ == '__main__':
    main()
