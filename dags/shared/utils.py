from airflow.utils.file import open_maybe_zipped


def read_packaged_file(fileloc):
    """
    Opens a plain file from a packages dag
    input as the relative path of the file to dag
    :return: str content of file
    """
    with open_maybe_zipped(fileloc, "r") as f:
        content = f.read()
    return content.decode("utf-8")
