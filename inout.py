import csv
import json
import os
import yaml

def read_yaml(filename):
    filename = _enforce_file_extension(filename, '.yml')

    with open(filename, 'r') as stream:
        try:
            return yaml.load(stream)
        except:
            raise

def read_csv(filename, delimiter=';', skip_header=True):
    filename = _enforce_file_extension(filename, '.csv')

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)

        if skip_header:
            next(reader, None)  #skipping header
        return list(reader)

def write_csv(filename, data, delimiter=';', newline=''):
    filename = _enforce_file_extension(filename, '.csv')

    _enforce_path(filename)
    with open(filename, 'w', newline=newline) as csvfile:
        csv.writer(csvfile, delimiter=delimiter).writerows(data)

def write_json(filename, data):
    filename = _enforce_file_extension(filename, '.json')

    text = json.dumps(data)

    _enforce_path(filename)
    with open(filename, 'w') as jsonfile:
        jsonfile.write(text)


##
#UTILS

def _enforce_file_extension(filename, extension):

    #enforcing that the extension name has a preceding dot
    extension = extension if extension[0] == '.' else '.' + extension

    file_extension = os.path.splitext(filename)[1]

    filename += '' if file_extension.lower() == extension.lower() else extension
    return filename

def _enforce_path(filename):

    filepath = os.path.dirname(filename)

    if filepath and not os.path.exists(filepath):
        os.makedirs(filepath)
