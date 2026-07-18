import unittest
from crawl import normalize_url, get_heading_from_html

class TestNormalizeUrl(unittest.TestCase):
    def test_normalize_url_with_https(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_with_trailing_slash(self):
        input_url = "www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_with_http(self):
        input_url = "http://www.boot.dev/blog"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog"
        self.assertEqual(actual, expected)

    def test_root_with_trailing_slash(self):
        input_url = "https://www.boot.dev/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

class TestExtractHTMLHeading(unittest.TestCase):
    def test_extract_h1_basic(self):
        html_doc = '''
            <html>
                <body>
                    <h1>Test Title</h1>
                </body>
            </html>

        '''
        actual = get_heading_from_html(html_doc)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_extract_h2_fallback(self):
        html_doc = '''
            <html>
                <body>
                    <h2>Test Fallback when no h1.</h2>
                </body>
            </html>

        '''
        actual = get_heading_from_html(html_doc)
        expected = "Test Fallback when no h1."
        self.assertEqual(actual, expected)

    def test_extract_nothing(self):
        html_doc = '''
            <html>
                <body>
                    <p>Paragraph only</p>
                </body>
            </html>

        '''
        actual = get_heading_from_html(html_doc)
        expected = ""
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()