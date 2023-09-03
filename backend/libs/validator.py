def check_optional_args(**kwargs):
    missing_args = list()
    for key, value in kwargs.items():
        if value is None:
            missing_args.append(key)
    return missing_args
