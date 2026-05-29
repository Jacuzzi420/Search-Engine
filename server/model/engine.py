from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from numpy.typing import NDArray
from scipy.sparse.linalg import svds
from scipy import sparse
import numpy as np
import joblib
import re

class Analyzer:
    def __init__(self):
        self.stop_words = get_stop_words()
        self.stemmer = PorterStemmer()

    def __call__(self, text: str):
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
    X = vectorizer.fit_transform(text)

    try:
        sparse.save_npz("model/saved/matrix.npz", X)
        joblib.dump(vectorizer, "model/saved/tfidf_vectorizer.pkl")
        joblib.dump(metadata, "model/saved/metadata.pkl")
    except Exception as e:
        print("Błąd zapisu modelu: ", e)

    print("Zapisano model")

def load_model(k: int) -> tuple[NDArray[np.float64], NDArray[np.float64], TfidfVectorizer, list[tuple[str, str]]]:
    try:
        matrix = sparse.load_npz("model/saved/matrix.npz")
        vectorizer = joblib.load("model/saved/tfidf_vectorizer.pkl")
        metadata = joblib.load("model/saved/metadata.pkl")
    except Exception as e:
        print("Błąd odczytu modelu: ", e)

    k = min(k, min(matrix.shape))
    U, S, Vt = svds(matrix, k)

    matrix = (matrix @ Vt.T).T
    matrix /= np.linalg.norm(matrix, axis=0)

    return matrix, Vt, vectorizer, metadata

def get_search(text: str, n: int, matrix: NDArray[np.float64], Vt: NDArray[np.float64], vectorizer: TfidfVectorizer, metadata: list[tuple[str, str]]) -> list[tuple[str, str]]:    
    q = vectorizer.transform([text])
    data, indices = q.data, q.indices

    if len(data) == 0:
        q = np.zeros(Vt.shape[0])
    else:
        q = data @ Vt.T[indices]
        q /= np.linalg.norm(q)

    dot_products = np.squeeze(q @ matrix)
    partition = np.argpartition(dot_products, -n)[-n:]
    indicies = partition[np.argsort(dot_products[partition])[::-1]]

    return [metadata[i] for i in indicies]