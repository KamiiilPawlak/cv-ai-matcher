# Instrukcja instalacji i uruchomienia

Istnieją dwie metody uruchomienia projektu: za pomocą **Dockera** (rekomendowana, stawia kompletne środowisko wraz z bazą danych i dokumentacją) lub **tradycyjna, lokalna** (wymaga samodzielnego skonfigurowania bazy PostgreSQL).

---

## 🐳 Metoda 1: Uruchomienie przez Docker (Rekomendowane)

Ta metoda automatycznie konfiguruje i uruchamia aplikację backendową (FastAPI), bazę danych (PostgreSQL) oraz serwer dokumentacji (MkDocs) w odizolowanych kontenerach.

### 1. Klonowanie repozytorium

Pobierz kod na swój dysk lokalny:

```bash
git clone [https://github.com/KamiiilPawlak/cv-ai-matcher.git](https://github.com/KamiiilPawlak/cv-ai-matcher.git)
cd cv-ai-matcher
```

### 2. Wymagania wstępne

Upewnij się, że masz zainstalowany i uruchomiony program Docker Desktop.

💡 Użytkownicy systemu Windows: Upewnij się, że w Menedżerze Zadań (zakładka Wydajność -> CPU) masz włączoną wirtualizację sprzętową oraz zainstalowany i zaktualizowany podsystem WSL2.

### 3. Uruchomienie całego stosu technologicznego

W głównym katalogu projektu (tam, gdzie znajduje się plik docker-compose.yml) wykonaj jedno z poniższych poleceń w terminalu:

- Uruchomienie w tle (zalecane):

```bash
docker compose up --build -d
```

- Uruchomienie z podglądem logów na żywo:

```bash
docker compose up --build
```

## 4. Lokalna weryfikacja działania środowiska

Po poprawnym zbudowaniu obrazów, uzyskasz dostęp do poszczególnych usług pod poniższymi adresami:

| Usługa                    | Adres URL                     | Opis                                                                                |
| :------------------------ | :---------------------------- | :---------------------------------------------------------------------------------- |
| **Backend API**           | <http://localhost:8000>       | Główny punkt dostępowy FastAPI                                                      |
| **Swagger UI**            | <http://localhost:8000/docs>  | Interaktywna dokumentacja z której będziemy ucuhamiać nasz CV AI Matcher endpointów |
| **ReDoc**                 | <http://localhost:8000/redoc> | Alternatywna dokumentacja API                                                       |
| **Dokumentacja projektu** | <http://localhost:8001>       | Serwer MkDocs (Material theme) z przeładowywaniem na żywo                           |

---

## 💻 Metoda 2: Tradycyjne uruchomienie lokalne (Deweloperskie)

Stosuj tę metodę, jeśli chcesz pracować bezpośrednio w lokalnym środowisku wirtualnym i posiadasz już zewnętrznie uruchomioną oraz skonfigurowaną bazę danych PostgreSQL.

### 1. Przygotowanie środowiska i instalacja zależności

Projekt zarządza zależnościami przez plik pyproject.toml. Utwórz środowisko wirtualne .venv i zainstaluj wymagane pakiety:

- windows

```shell
python -m venv .venv
.\.venv\Scripts\activate
pip install .

```

- linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .

```

### 2. Konfiguracja bazy danych

Przed uruchomieniem serwera upewnij się, że posiadasz działającą instancję bazy PostgreSQL oraz ustaw odpowiednią zmienną środowiskową (np. w pliku .env lub bezpośrednio w systemie):

```plaintext
DATABASE_URL=postgresql://<USER>:<PASSWORD>@localhost:5432/<DB_NAME>
```

### 3. Uruchomienie aplikacji (Uvicorn)

Przejdź do katalogu aplikacji backendowej i uruchom serwer z flagą automatycznego przeładowywania kodu po zapisie zmian (--reload):

```bash
cd backend
uvicorn app.main:app --reload

```

Aplikacja oraz dokumentacja Swagger/ReDoc będą wtedy dostępne lokalnie pod adresem `http://127.0.0.1:8000`.
