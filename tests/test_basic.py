import os
import unittest


class TestProjectSetup(unittest.TestCase):

    def test_config_directory_exists(self):
        """التحقق من وجود مجلد الإعدادات config"""
        self.assertTrue(os.path.exists("config"), "مجلد config غير موجود")

    def test_app_directory_exists(self):
        """التحقق من وجود مجلد التطبيق app"""
        self.assertTrue(os.path.exists("app"), "مجلد app غير موجود")


if __name__ == "__main__":
    unittest.main()
