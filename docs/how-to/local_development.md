## 🛠️ Krok 1: Klonowanie repozytorium

Pobierz aktualną wersję kodu na swój dysk lokalny za pomocą systemu Git:

```bash
git clone https://github.com/KamiiilPawlak/cv-ai-matcher.git
cd <NAZWA_FOLDERU_PROJEKTU>
```

## 📦 Krok 2: Przygotowanie środowiska i instalacja zależności

Projekt zarządza zależnościami przez plik pyproject.toml. Uruchom poniższe komendy, aby utworzyć środowisko wirtualne .venv i zainstalować wymagane pakiety:

- Windows:

```shell
python -m venv .venv
.\.venv\Scripts\activate
pip install .
```

- Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Krok 3: Uruchomienie aplikacji (Uvicorn)

Przejdź do katalogu aplikacji backendowej i uruchom serwer deweloperski Uvicorn z flagą automatycznego przeładowywania kodu po zapisie zmian `(--reload)`:

```shell
cd backend
uvicorn main:app --reload
```

## 🌐 Krok 4: Lokalna weryfikacja działania aplikacji

Gdy serwer wystartuje, backend jest gotowy pod adresem:

    http://127.0.0.1:8000

Automatycznie generowana interaktywna dokumentacja API oraz endpointów jest dostępna pod adresami:

    Swagger UI: http://127.0.0.1:8000/docs

    ReDoc: http://127.0.0.1:8000/redoc

## 🐳 Docker (W przygotowaniu)

Obecnie trwają prace nad pełną konteneryzacją całego stosu technologicznego przy użyciu Dockera oraz Docker Compose.

Po zakończeniu konfiguracji uruchomienie backendu, bazy danych oraz powiązanych kontenerów będzie możliwe za pomocą jednej komendy systemowej:

```shell
docker-compose up --build
```
