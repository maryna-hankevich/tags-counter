import unittest

from app import get_full_url, get_tags_num, get_tags_num_from_db


class TagsCounterTestCase(unittest.TestCase):
    def test_full_url_from_alias(self):
        yandex_url = get_full_url("ydx")
        expected_yandex_url = 'https://yandex.ru'
        self.assertEqual(yandex_url, expected_yandex_url)

    def test_full_url_with_https(self):
        yandex_url = get_full_url("https://yandex.ru")
        expected_yandex_url = 'https://yandex.ru'
        self.assertEqual(yandex_url, expected_yandex_url)

    def test_full_url_without_http(self):
        yandex_url = get_full_url("yandex.ru")
        expected_yandex_url = 'https://yandex.ru'
        self.assertEqual(yandex_url, expected_yandex_url)

    def test_compare_tags_num(self):
        tags_num = get_tags_num("google.com")
        tags_num_from_db = get_tags_num_from_db("google.com")
        self.assertEqual(tags_num, tags_num_from_db)


if __name__ == '__main__':
    unittest.main()
