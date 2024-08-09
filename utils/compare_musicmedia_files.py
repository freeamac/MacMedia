#! /usr/bin/env python3

import click

def parse_musicmedia_blobs(filepath):

    musicmedia_blobs = {}
    in_blob = False
    blob = []
    with open(filepath, 'r') as fd:
        for line in fd.readlines():
            if line.startswith('<p>'):
                in_blob = True
            elif line.startswith('</p>'):
                in_blob = False
                blob_key = ''.join([x.strip() for x in blob[:3]])
                musicmedia_blobs[blob_key] = blob
                blob = []
            elif in_blob:
                blob.append(line.replace('\n', ''))

    return musicmedia_blobs

@click.command('Compare music media blobs in two music media html files.')
@click.option('-1', '--filepath1', type=str, required=True, help='First music media html file.')
@click.option('-2', '--filepath2', type=str, required=True, help='Second music media html file.')
def compare_files(filepath1 = None, filepath2 = None):
    musicmedia_blobs1 = parse_musicmedia_blobs(filepath1)
    musicmedia_blobs2 = parse_musicmedia_blobs(filepath2)

    for blob1_key, blob1 in musicmedia_blobs1.items():
        try:
            blob2 = musicmedia_blobs2[blob1_key]
            for line_no, line in enumerate(blob1):
                try:
                    if line != blob2[line_no]:
                        print('  {}[1 {}] : {}'.format(blob1_key, line_no, line))
                        print('  {}[2 {}] : {}'.format(blob1_key, line_no, blob2[line_no]))
                except IndexError:
                    pass  # Case where extra infor in blob1
            if len(blob1) > len(blob2):
                for line in blob1[len(blob2):]:
                    print('  {}[extra 1]{}'.format(blob1_key, line))
            if len(blob2) > len(blob1):
                for line in blob1[len(blob1):]:
                    print('  {}[extra 2]{}'.format(blob1_key, line))
            del musicmedia_blobs2[blob1_key]
        except KeyError:
            print('  {}[missing 2]'.format(blob1_key))

    for blob2_key in musicmedia_blobs2.keys():
        print('  {}[missing 1]'.format(blob2_key))

if __name__ == '__main__':
  compare_files()
