from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from numpy.typing import NDArray
import numpy as np
import joblib
import re

class Analyzer:
    def __init__(self):
        self.stop_words = get_stop_words()
        self.stemmer = PorterStemmer()

    def __call__(self, text):
        tokens = []

        for token in re.findall(r"\b\w+\b", text):
            token_lower = token.lower()
            if token_lower not in self.stop_words: tokens.append(self.stemmer.stem(token_lower, False))

        return tokens

def get_stop_words() -> set[str]:
    stop_words = set()

    try:
        with open('model/stop_words_english.txt', 'r') as f:
            for line in f.readlines():
                stop_words.add(line.strip())
    except FileNotFoundError:
        print("Nie znaleziono pliku")
    except UnicodeDecodeError:
        print("Złe kodowanie")

    return stop_words

def get_search_data() -> tuple[list[str], list[str], list[str]]:
    files = []
    titles = []
    urls = []

    try:
        with open('data/description.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                file, title, url = line.split('|')
                files.append(file.strip() + ".txt")
                titles.append(title.strip())
                urls.append(url.strip())

    except FileNotFoundError:
        print("Nie znaleziono pliku")
    except UnicodeDecodeError:
        print("Złe kodowanie")

    text = []

    try:
        for file in files:
            with open(f'data/{file}', 'r', encoding='utf-8') as f:
                text.append(f.read())

    except FileNotFoundError:
        print("Nie znaleziono pliku")
    except UnicodeDecodeError:
        print("Złe kodowanie")

    return text, titles, urls

def save_model(text: list[str], metadata: list[tuple[str, str]]) -> None:
    analyzer = Analyzer()
    vectorizer = TfidfVectorizer(analyzer=analyzer)
    X = vectorizer.fit_transform(text).toarray().transpose()
    U, S, Vt = np.linalg.svd(X, full_matrices=False)

    try:
        np.savez("model/saved/svd.npz", U=U, S=S, Vt=Vt)
        joblib.dump(vectorizer, "model/saved/tfidf_vectorizer.pkl")
        joblib.dump(metadata, "model/saved/metadata.pkl")
    except Exception as e:
        print("Błąd zapisu modelu: ", e)

def load_model(k: int) -> tuple[TfidfVectorizer, NDArray[np.float64], list[tuple[str, str]]]:
    try:
        svd = np.load("model/saved/svd.npz")
        vectorizer = joblib.load("model/saved/tfidf_vectorizer.pkl")
        metadata = joblib.load("model/saved/metadata.pkl")
    except Exception as e:
        print("Błąd odczytu modelu: ", e)

    U, S, Vt = svd['U'], svd['S'], svd['Vt']
    k = min(k, S.shape[0])

    matrix = (U[:, :k] * S[:k]) @ Vt[:k, :]
    norms = np.linalg.norm(matrix, axis=0)
    return matrix / norms, vectorizer, metadata

def get_search(text: str, matrix: NDArray[np.float64], vectorizer: TfidfVectorizer, metadata: list[tuple[str, str]]):
    q = vectorizer.transform([text]).toarray()
    dot_products = np.squeeze(q @ matrix)
    print(np.partition(dot_products, -5)[-5:])
    return np.argpartition(dot_products, -5)[-5:]

if __name__ == "__main__":
    text, titles, urls = get_search_data()
    save_model(text, zip(titles, urls))
    matrix, vectorizer, metadata = load_model(10)
    print(get_search("Apollo program", matrix, vectorizer, metadata))