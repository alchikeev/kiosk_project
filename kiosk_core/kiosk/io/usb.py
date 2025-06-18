import os
from getpass import getuser

def get_usb_mount_path():
    """
    Возвращает список смонтированных путей USB-носителей в /media/<user>/
    """
    media_root = f"/media/{getuser()}"
    if not os.path.exists(media_root):
        return []
    
    devices = []
    for device in os.listdir(media_root):
        full_path = os.path.join(media_root, device)
        if os.path.ismount(full_path):
            devices.append(full_path)
    return devices


def list_usb_documents(extensions=None):
    """
    Возвращает список документов с USB-флешек, подходящих для печати.

    :param extensions: список допустимых расширений, например [".pdf", ".docx"]
    :return: список полных путей к файлам
    """
    if extensions is None:
        extensions = [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf"]

    found_files = []
    usb_mounts = get_usb_mount_path()

    for mount_point in usb_mounts:
        for root, _, files in os.walk(mount_point):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    found_files.append(os.path.join(root, file))
    
    return found_files


# Для отладки: запуск напрямую
if __name__ == "__main__":
    docs = list_usb_documents()
    if not docs:
        print("Флешка не найдена или нет документов.")
    else:
        print("Найденные документы:")
        for doc in docs:
            print(f"- {doc}")
