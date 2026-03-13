
def test_pass_for_video(page):
    page.goto("https://www.google.com")
    assert page.title() == "Google"
