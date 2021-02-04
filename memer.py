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
        found_files = 0
        meme_img = None
        Memer.clear_dir()
        while found_files < 15:  # looking for good picture
            meme_response = requests.request(method='Get', url='https://meme-api.herokuapp.com/gimme')
            meme_json = meme_response.json()
            filename = meme_json['url'].split("/")[-1]
            filename = os.path.join(MEMES_TO_SAVE_PATH, filename)
            wget.download(meme_json['url'], filename)
            file_stats = os.stat(filename)
            file_ext = filename.split('.')[-1]
            if file_ext.lower() in ('jpg', 'jpeg', 'png', 'gif') and file_stats.st_size < 5 * BYTES_IN_MB:
                meme_img = open(filename, 'rb')
                break
            print(f'File did not pass conditions ext: {file_ext}, size: {file_stats.st_size / BYTES_IN_MB} mb')
            found_files += 1
        return meme_img

    @staticmethod
    def clear_dir():
        for file in os.listdir(MEMES_TO_SAVE_PATH):
            os.remove(os.path.join(MEMES_TO_SAVE_PATH, file))


    @staticmethod
    def get_random_wendesday():
        pict_path = os.path.join(WEDNESDAY_MEMES_PATH, Memer.get_random_file(WEDNESDAY_MEMES_PATH))
        img = open(pict_path, 'rb')
        print(f'Got random pict {pict_path}')
        return img

    @staticmethod
    def get_random_file(dir_path):
        return random.choice(os.listdir(dir_path))
