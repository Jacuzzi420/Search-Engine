# Search-Engine

Dane do wyszukiwarki zostały zescrapowane za pomocą webcrawlera. Jako seedy do crawlera wykorzystałem głównie adresy artykułów o celebrytach lub politykach z oryginalnej anglojęzycznej wikipedii. Do wydobywania najważniejszych informacji z dokumentu HTML, wykorzystałem bibliotekę `trafilatura`.

## Model wyszukiwania

Jako sam search engine wykorzystałem gotowy model TF-IDF z biblioteki `scikit-learn` i faktoryzację SVD. Słowa z dokumentów są stemmowane algorytmem PorterStemmer z biblioteki `nltk`. Usuwam również angielskie stop-words.

Do obliczania SVD wykorzystałem funkcję svds z biblioteki `scipy`, która przybliża pierwsze $k$ wartości osobliwych.

Ponieważ przybliżanie oryginalnej macierzy w ten sposób było zbyt kosztowne pamięciowo:

$$
A \simeq A_k = U_k D_k V^{T}
$$

zdecydowałem się na redukcję wymiarów z wykorzystaniem SVD:

$$
A_{\text{zredukowana}} = U_k D_k = A V
$$

ponieważ $V$ jest ortogonalna, tzn.

$$
V V^{T} = I, \quad V^{T} = V^{-1}
$$

Stosując redukcję wymiarów, muszę również zmienić wymiar wektora zapytania, więc:

$$
q = q V
$$

Wektor $q$ jest rzadki, więc można te mnożenie zoptymalizować, co znacznie przyspieszyło zapytania do wyszukiwarki.

Oczywiście wektor $q$ jest normalizowany, oraz wektory odpowiadające dokumentom w $A_{\text{zredukowana}}$ również.

## Embeddingi semantyczne

Model TF-IDF z SVD wspieram również semantycznimi embeddingami.

Najpierw chunkuje wszystkie dokumenty rekurencyjnie (całe dokumenty przekraczały limit tokenów), a następnie wektoryzuje chunki za pomocą modeleu `nomic-embed-text`. Do rekurencyjnego chunkowania skorzystałem z RecursiveChunker z biblioteki `chonkie`.

Do przechowywania wektorów wybrałem bazę wektorową Qdrant.

## Frontend i API

Frontend jest napisany w `react`, natomiast api do wyszukiwarki w `fastapi`.