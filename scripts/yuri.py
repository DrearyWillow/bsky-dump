from pathlib import Path

input_path = Path("/home/kyler/Downloads/swag/hype.txt")
if not input_path.is_dir():
    if input_path.parent.is_dir():
        input_dir = str(input_path.parent)
        input_filename = input_path.stem
        print("DIR: " + input_dir)
        print("FN: " + input_filename)
    else:
        print(f"not a valid directory")
else:
    print("huh? how?")
