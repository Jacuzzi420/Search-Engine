from model.engine import get_search_data, save_model

if __name__ == "__main__":
    text, titles, urls = get_search_data()
    save_model(text, list(zip(titles, urls)))