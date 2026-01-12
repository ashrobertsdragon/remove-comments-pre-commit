import unittest
from remove_comments import remove_python_comments, remove_c_style_comments, remove_hash_comments

class TestRemoveComments(unittest.TestCase):
    def test_python_inline_comment(self):
        source = "x = 1 # comment"
        expected = "x = 1"
        self.assertEqual(remove_python_comments(source), expected)

    def test_python_full_line_comment(self):
        source = "# comment\nx = 1"
        expected = "\nx = 1"
        self.assertEqual(remove_python_comments(source), expected)

    def test_python_comment_in_string(self):
        source = 's = "# not a comment"'
        expected = 's = "# not a comment"'
        self.assertEqual(remove_python_comments(source), expected)

    def test_python_docstring(self):
        source = '"""\nThis is a docstring.\n# comment inside\n"""'
        expected = '"""\nThis is a docstring.\n# comment inside\n"""'
        self.assertEqual(remove_python_comments(source), expected)

    def test_c_style_inline(self):
        source = "int x = 1; // comment"
        expected = "int x = 1;"
        self.assertEqual(remove_c_style_comments(source), expected)

    def test_c_style_string(self):
        source = 'char* s = "// not comment";'
        expected = 'char* s = "// not comment";'
        self.assertEqual(remove_c_style_comments(source), expected)

    def test_c_style_doc_comment(self):
        # Java/JS doc
        source = "/**\n * Doc\n */\nint x = 1;"
        expected = "/**\n * Doc\n */\nint x = 1;"
        self.assertEqual(remove_c_style_comments(source), expected)

    def test_rust_doc_comment(self):
        source = "/// Doc line\nfn main() {}"
        expected = "/// Doc line\nfn main() {}"
        self.assertEqual(remove_c_style_comments(source), expected)
        
    def test_rust_mod_doc_comment(self):
        source = "//! Module doc\n"
        expected = "//! Module doc\n"
        self.assertEqual(remove_c_style_comments(source), expected)

    def test_c_style_block_comment_preservation(self):
        # We decided to preserve block comments /* ... */ unless they are explicitly targeted?
        # My implementation preserves them if they match doc block or if they are just block comments 
        # because I only target `//` in the removal group?
        # Wait, looking at regex: `pattern_doc_block = r"/\*[\*!].*?\*/"` -> matches /** or /*!
        # Normal /* ... */ is NOT matched by doc block.
        # It is NOT matched by strings.
        # It is NOT matched by inline comment `//`.
        # So it falls through and is PRESERVED.
        source = "/* Ordinary block comment */\nint x = 1;"
        expected = "/* Ordinary block comment */\nint x = 1;"
        self.assertEqual(remove_c_style_comments(source), expected)

    def test_hash_style_inline(self):
        source = "var: value # comment"
        expected = "var: value"
        self.assertEqual(remove_hash_comments(source), expected)

    def test_hash_style_string(self):
        source = 'key: "# not comment"'
        expected = 'key: "# not comment"'
        self.assertEqual(remove_hash_comments(source), expected)

if __name__ == "__main__":
    unittest.main()
