import os, sys, glob, csv, argparse

REPLACED_PATH = "./replaced"


def get_replacing_dict(template_path):
    """Get a dictionary of the headers that has dot notations and their corresponding underscore notations"""
    external_file_path = f"{template_path}/external_files"

    print("External files path:", external_file_path)

    headers_with_dots = set()

    # Iterate over every file in the external_files directory
    for filename in glob.glob(os.path.join(external_file_path, '*.csv')):
        reader = csv.DictReader(open(filename))

        # Get headers with dot notations
        with_dots = filter(lambda header: '.' in header, reader.fieldnames)

        # Initial replacements could the next replacements from working (E.g. Product.Name replaced for Product_Name prevents Parent.Account.Name from being replaced since it's now Parent.Account_Name)
        # Split and replace every word.word combination in the headers
        for field in with_dots:
            field_arr = field.split(".")
            for j in range(len(field_arr) - 1):
                combination = '.'.join((field_arr[j], field_arr[j+1]))
                headers_with_dots.add(combination)

    print("Headers are:", headers_with_dots)
    
    replacing_dict = {header: header.replace(
        '.', '_') for header in headers_with_dots}

    return replacing_dict


def replace_dot_notations(template_path, type, replacing_dict, storing_path):
    """Replace the dot notations for a type of files (dashboards, XMDs, dataflows, lenses)"""
    files_path = f"{template_path}/{type}"

    # Create a folder for the specific type of files
    replaced_inner_path = f"{storing_path}/{type}"
    if not os.path.exists(replaced_inner_path):
        os.mkdir(replaced_inner_path)

    print(f"Replacing dot notations in {type}")
    # Iterate over the files in the specific type directory
    for pathname in glob.glob(os.path.join(files_path, '*')):
        
        filename = pathname[len(files_path):]

        with open(pathname, 'r') as file:
            filedata = file.read()

        for original, replace in replacing_dict.items():
            filedata = filedata.replace(original, replace)

        with open(f"{replaced_inner_path}/{filename}", 'w+') as file:
            file.write(filedata)


def run(args):
    replacing_dict = get_replacing_dict(args.path)

    # Create folder to store new files
    if not os.path.exists(REPLACED_PATH):
        os.mkdir(REPLACED_PATH)

    replace_dot_notations(args.path, "dashboards", replacing_dict, REPLACED_PATH)
    if args.xmds:
        replace_dot_notations(args.path, "dataset_files", replacing_dict, REPLACED_PATH)
    if args.dataflow:
        replace_dot_notations(args.path, "dataflow", replacing_dict, REPLACED_PATH)
    if args.lenses:
        replace_dot_notations(args.path, "lenses", replacing_dict, REPLACED_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='replace_dot_notations', description='Replace dot notations for dataset fields in dashboards, and optionally XMDs, dataflows and lenses.')

    parser.add_argument('-p', '--path', type=str, required=True,
                        help="Specify the path of the template that needs dot notation replacement.")
    parser.add_argument('-x', '--xmds', default=False, action='store_true',
                        help="Include if dot notation needs to be fixed for XMDs.")
    parser.add_argument('-d', '--dataflow', default=False, action='store_true',
                        help="Include if dot notation needs to be fixed for dataflows.")
    parser.add_argument('-l', '--lenses', default=False, action='store_true',
                        help="Include if dot notation needs to be fixed for lenses.")

    run(parser.parse_args())