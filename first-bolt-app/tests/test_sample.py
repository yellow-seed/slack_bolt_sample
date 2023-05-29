# content of test_sample.py
def inc(x):
    return x + 1


# testコードはtest_で始まる関数名をつける test_で始まらないものはtestコードとみなされない
def test_always_true():
    assert 5 == 5
