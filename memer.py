import aiohttp
import os
import random
import wget

MEME_API = 'https://meme-api.herokuapp.com/gimme'
WEDNESDAY_MEMES_PATH = 'images/wednesday'
MEMES_TO_SAVE_PATH = 'images/memes'
BYTES_IN_MB = 1000000


class Memer:
    """Класс для доступа к мемам.

    Также включает другие фишки.
    """
    async def get_random_meme(self):
        self._clear_dir()
        async with aiohttp.ClientSession() as session:

            meme_url = 'https://meme-api.herokuapp.com/gimme'
            async with session.get(meme_url) as meme_response:
                meme_json = await meme_response.json()

        filename = meme_json['url'].split("/")[-1]
        filename = os.path.join(MEMES_TO_SAVE_PATH, filename)
        wget.download(meme_json['url'], filename)
        meme_img = open(filename, 'rb')
        file_ext = filename.split('.')[-1]
        return meme_img, file_ext

    def _clear_dir(self):
        for file in os.listdir(MEMES_TO_SAVE_PATH):
            try:
                os.remove(os.path.join(MEMES_TO_SAVE_PATH, file))
            except PermissionError:
                pass

    def get_random_wednesday(self):
        """Получить случайный мем про среду.

        Используется локальной хранилище мемов

        Returns:
            Изображение с мемом
        """
        pict_path = os.path.join(WEDNESDAY_MEMES_PATH, Memer.get_random_file(WEDNESDAY_MEMES_PATH))
        img = open(pict_path, 'rb')
        print(f'Got random pict {pict_path}')
        return img

    def get_random_file(self, dir_path):
        """Получить путь до случайного файла из директории.

        Args:
            dir_path: Директория для поиска файла

        Returns:

        """
        return random.choice(os.listdir(dir_path))

    async def generate_text(self, text):
        """Сгенерировать случайный текст на основе части.

        Используется нейронная сеть яндекс

        Args:
            text: Часть текста

        Returns:
            Сгенерированный текст
        """
        async with aiohttp.ClientSession() as session:

            url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'
            body = {'text': text}
            async with session.post(url=url, json=body) as predict_text_resp:
                if predict_text_resp.status == 200:
                    text_json = await predict_text_resp.json()
                    return text_json['predictions']
                else:
                    return f'Got non 200 response: {predict_text_resp.status}'
