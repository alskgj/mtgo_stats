import json
import pathlib

import httpx

targets = [
    {
        'url': 'https://www.mtgo.com/decklist/pioneer-challenge-64-2024-07-0812655622',
        'description': 'Pioneer Challenge 64',
        'filename': 'response_tournament_challenge_64'
     }
]


def extract_json_data(tournament_data: str) -> str:
    for line in tournament_data.split('\n'):
        if 'window.MTGO.decklists.data' in line:
            return line.strip().split(' = ')[1].strip(";")

    raise ValueError('Could not find census link in tournament data.')


def main():
    for target in targets:
        print(f'Downloading {target}')
        res = httpx.get(target['url'])
        if res.status_code != 200:
            print(f'Failed downloading {target}')
            continue
        result = f"""
        <!-- {target['description']} -->
        <!-- {target['url']} -->""" + res.text
        with open(pathlib.Path() / (target['filename'] + ".html"), 'w') as fo:
            fo.write(result)

        with open(pathlib.Path() / (target['filename'] + ".json"), 'w') as fo:
            fo.write(extract_json_data(res.text))


if __name__ == '__main__':
    main()
