import unittest
import warnings

from views.reddit.analyzereddit import setup_reddit
from views.facebook.analyzepage import facebook_login_check, facebook_login
from views.twitter.analyzetwitter import setup_twitter


class TestStringMethods(unittest.TestCase):
    def test_check_facebook_login(self):
        print("Checking successful facebook login:")
        self.assertEqual("ok", facebook_login_check())

    def test_check_reddit_login(self):  
        print("Checking successful reddit login:")
        self.assertNotEqual("NULL", setup_reddit())

    def test_check_twitter_login(self):
        print("Checking successful twitter login:")
        self.assertNotEqual("NULL", setup_twitter())

    def test_valid_page(self):
        print("Checking valid facebook page:")
        self.assertEqual("Not valid", facebook_login("https://mobile.facebook.com/" + "stl" + "/"))


if __name__ == '__main__':
    warnings.filterwarnings(action="ignore", message="unclosed",
                            category=ResourceWarning)
    unittest.main()



