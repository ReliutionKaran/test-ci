import os
import ast

ROOT_PATH = "/mnt/extra-addons/custom-addons"
def prepare_python_libraries():
    current_directories = os.listdir(path=ROOT_PATH)
    print(f"Root Directories : {current_directories}")
    manifest_file_list = []
    libraries_list = []
    get_manifest_directories(ROOT_PATH, manifest_file_list, current_directories)
    print(f"Manifest File List : {manifest_file_list}")

    for file_path in manifest_file_list:
        print("File Path : " file_path)
        libraries_info = extract_manifest_keys(file_path)
        libraries_listextend(libraries_info)
        create_requirements(libraries_list)
    print(f"All External Dependency List : {list(set(libraries_list))}")

def get_manifest_directories(path, manifest_file_list, current_directories):
    for directory_info in current_directories:
        if (not directory_info.startswith(".") and not directory_info.endswith(
                (".folder", ".file", ".zip", ".md", ".txt", ".git", ".gitignore", ".png",".rar", ".csv", ".xml"))):
            dir_path = os.path.join(path, directory_info)
            if os.path.isdir(dir_path):
            	list_dir = os.listdir(dir_path)
            else:
            	list_dir = dir_path
            	if list_dir.__contains__('__manifest__.py'):
            		manifest_file_list.append(list_dir)
            print(f"Directory : {dir_path}, Files & Folders : {list_dir}")
            if list_dir.__contains__('__manifest__.py'):
                for manifest_file in list_dir:
                    if manifest_file == '__manifest__.py':
                        manifest_file_list.append(os.path.join(dir_path, manifest_file))
            else:
            	if os.path.isdir(dir_path):
                	get_manifest_directories(dir_path, manifest_file_list, os.listdir(dir_path))
    return manifest_file_list

def extract_manifest_keys(manifest_file_path):
    """Extracts the Python key array from an Odoo manifest.py file.

    Args:
        manifest_file_path (str): The path to the manifest.py file.

    Returns:
        list: A list of Python keys extracted from the manifest file.
    """

    with open(manifest_file_path, "r", encoding="utf-8") as manifest_file:
        manifest_data = manifest_file.read()

    # Parse the manifest file as a Python AST
    tree = ast.parse(manifest_data)

    values = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for node_key, node_value in zip(node.keys, node.values):
                if node_key.value == "external_dependencies":
                    values = node_value
                    break

    # Extract the keys from the assignment node
    if isinstance(values, ast.Dict) and values.values:
        keys_value = values.values[0]
        if isinstance(keys_value, ast.List):
            return [elt.s for elt in keys_value.elts]
        else:
            raise ValueError("Invalid keys value in manifest.py")
    return []

def create_requirements(libraries_list):
    requirements = open('requirements.txt', 'w+')
    for lib_name in list(set(libraries_list)):
        requirements.write(lib_name+';'+"\n")
        print(requirements)

prepare_python_libraries()
