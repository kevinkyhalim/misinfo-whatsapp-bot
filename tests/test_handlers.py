from app.handlers import process_incoming_message

def test_text_input():
    response = process_incoming_message("Is COVID-19 spread by 5G?")
    assert "misinformation" in response.lower()

def test_link_input():
    response = process_incoming_message("https://randomsite.com/news/fake-article")
    assert "url" in response.lower()
