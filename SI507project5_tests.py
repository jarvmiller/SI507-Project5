import unittest
import json
from SI507project5_code import *


class TEST_CACHE(unittest.TestCase):
    def test_cache_type(self):
        self.assertTrue(isinstance(HARVEY_CACHE_DICTION, dict))
        self.assertTrue(isinstance(CONCERT_CACHE_DICTION, dict))



class TEST_EVENT(unittest.TestCase):
    def setUp(self):
        with open('test_cache_contents.json', 'r') as f:
            cache_json = f.read()
            event_diction = json.loads(cache_json)
        self.event_list = [Event(event) for event in event_diction.values()]
        self.event = self.event_list[0]

    def test_event_list(self):
        [self.assertTrue(isinstance(event, Event)) for event in self.event_list]

    def test_init(self):
        self.assertTrue(self.event.id == '39130956745')
        self.assertTrue(self.event.name == 'Hurricane Harvey Benefit Concert')
        self.assertFalse(self.event.is_free)
        self.assertTrue(self.event.url == "https://www.eventbrite.com/e/hurricane-harvey-benefit-concert-tickets-39130956745?aff=ebapi")


    def test_str(self):
        self.assertEqual(self.event.__str__(),
                         "39130956745: Hurricane Harvey Benefit Concert")


class TEST_CSVS(unittest.TestCase):
    def setUp(self):
        self.harvey = open('harvey.csv')
        self.concert = open('um_concert.csv')

    def test_csv_files_exist(self):
        self.assertTrue(self.harvey.read())
        self.assertTrue(self.concert.read())

    def tearDown(self):
        self.harvey.close()
        self.concert.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
