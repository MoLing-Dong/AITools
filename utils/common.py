def append_file_content(file_path, formatted_list, role="assistant"):
    """
    读取文件内容，并以指定角色添加到 formatted 列表中。

    :param file_path: 文件路径
    :param formatted_list: 要添加的列表对象
    :param role: 消息角色，默认为 assistant
    :return: 成功与否的状态
    """
    import os

    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            formatted_list.append({"role": role, "content": content})
            return True
        else:
            print(f"Warning: {file_path} is empty.")
            return False
