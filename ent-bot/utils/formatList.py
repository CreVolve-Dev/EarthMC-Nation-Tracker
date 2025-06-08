def format_list(list, start=None, end=None):

    if start:
        names = [item['name'] for item in list[start:end] if 'name' in item]
        formatted_list = '\n'.join(f"- {name}" for name in names)
        return formatted_list
    else:
        names = [item['name'] for item in list if 'name' in item]
        formatted_list = '\n'.join(f"- {name}" for name in names)
        return formatted_list