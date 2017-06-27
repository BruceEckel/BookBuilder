#! py -3
# Utilities
import shutil


def clean(dir_to_remove):
    "Remove directory"
    try:
        if dir_to_remove.exists():
            shutil.rmtree(str(dir_to_remove))
            return "Removed: {}".format(dir_to_remove)
        else:
            return "Doesn't exist: {}".format(dir_to_remove)
    except Exception as e:
        print("""Removal failed: {}
        Are you inside that directory, or using a file inside it?
        """.format(dir_to_remove))
        print(e)


