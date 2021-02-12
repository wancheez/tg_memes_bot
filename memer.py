import requests
import os
import random
import wget

MEME_API = 'https://meme-api.herokuapp.com/gimme'
WEDNESDAY_MEMES_PATH = 'images/wednesday'
MEMES_TO_SAVE_PATH = 'images/memes'
BYTES_IN_MB = 1000000


class Memer:
    @staticmethod
    def get_random_meme():
        Memer.clear_dir()
        meme_response = requests.request(method='Get', url='https://meme-api.herokuapp.com/gimme')
        meme_json = meme_response.json()
        filename = meme_json['url'].split("/")[-1]
        filename = os.path.join(MEMES_TO_SAVE_PATH, filename)
        wget.download(meme_json['url'], filename)
        meme_img = open(filename, 'rb')
        return meme_img

    @staticmethod
    def clear_dir():
        for file in os.listdir(MEMES_TO_SAVE_PATH):
            try:
                os.remove(os.path.join(MEMES_TO_SAVE_PATH, file))
            except PermissionError:
                pass



    @staticmethod
    def get_random_wendesday():
        pict_path = os.path.join(WEDNESDAY_MEMES_PATH, Memer.get_random_file(WEDNESDAY_MEMES_PATH))
        img = open(pict_path, 'rb')
        print(f'Got random pict {pict_path}')
        return img

    @staticmethod
    def get_random_file(dir_path):
        return random.choice(os.listdir(dir_path))
