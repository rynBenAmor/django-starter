def normalize_dict_reader(reader):
    """
    Defines a generator that normalizes keys in a CSV DictReader to lowercase and strips whitespace.
    usage:
        for row in normalize_dict_reader(reader):
            ref = row.get('name')
            price = row.get('price')
    """
    reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
    for row in reader:
        yield {k.strip().lower(): v for k, v in row.items()}

