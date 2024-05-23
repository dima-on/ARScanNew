import json

def save_json(file_name, data):
    """
    data = {
            cloth: [[]]
            name: [@tg_tag]
            }
    :param file_name:
    :param data:
    :return:
    """
    file_path = "order/" + file_name

    with open(file_path, "w") as json_file:
        json.dump(data, json_file)

def save_json_All(file_name, data):
    """
    data = {
            cloth: [[]]
            name: [@tg_tag]
            }
    :param file_name:
    :param data:
    :return:
    """

    with open(file_name, "w") as json_file:
        json.dump(data, json_file)

def open_json(file_name):
    file_path = "order/" + file_name
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    return data
def open_jsonAll(file_name):
    with open(file_name, "r") as json_file:
        data = json.load(json_file)

    return data

def clear_json(file_name):
    file_path = "order/" + file_name
    data = {
        "cloth": [],
        "name": []
    }
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)


def main():
    pass

if __name__ == '__main__':
    main()