import os
from io import BufferedReader
from unittest.mock import patch
import json
from shutil import copyfile

from memer import Memer

MEMES_WORK_DIR = 'tests\\files'
MEMES_SOURCE_DIR = 'tests\\test_files'


def add_meme_to_dir(*args, **kwargs):
    copyfile(
        os.path.join(MEMES_SOURCE_DIR, 'fake_meme.jpg'),
        os.path.join(MEMES_WORK_DIR, 'fake_meme.jpg'),
    )


@patch('memer.MEMES_TO_SAVE_PATH', MEMES_WORK_DIR)
@patch('memer.wget.download', add_meme_to_dir)
def test_get_random_meme(requests_mock):
    memer_obj = Memer()
    meme_get_result = {
        "postLink": "https://fake_meme.jpg",
        "subreddit": "memes",
        "title": "Meme",
        "url": "https://fake_meme.jpg",
        "nsfw": False,
        "spoiler": False,
        "author": "Wancheez",
    }
    requests_mock.get('https://meme-api.herokuapp.com/gimme', text=json.dumps(meme_get_result))
    meme, ext = memer_obj.get_random_meme()
    assert meme
    assert isinstance(meme, BufferedReader)
    assert meme.name == 'tests\\files\\fake_meme.jpg'
    assert ext == 'jpg', 'Wrong file format'


def test_generate_text_success(requests_mock):
    generate_text_response = {
        'predictions': 'Testing this.'
    }
    requests_mock.post(
        'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict',
        text=json.dumps(generate_text_response),
        status_code=200,
    )
    result_text = Memer.generate_text('test')
    assert result_text == 'Testing this.'


def test_generate_text_failed(requests_mock):
    generate_text_response = {
        'predictions': 'Testing this.'
    }
    requests_mock.post(
        'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict',
        json=generate_text_response,
        status_code=404,
    )
    result_text = Memer.generate_text('test')
    assert result_text == 'Got exception from api: 404'
