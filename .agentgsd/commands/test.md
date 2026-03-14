---
name: test
description: Generate unit tests for the given file or function
---

Generate comprehensive unit tests for the file(s) provided in arguments.

Requirements:
1. Use pytest as the testing framework
2. Include both positive and negative test cases
3. Mock external dependencies appropriately
4. Follow the existing test file naming conventions ($FILE should have corresponding test_$FILE or $FILE_test.py)
5. Add docstrings to each test function
6. Ensure tests are runnable with: pytest $SELECTED_FILES
