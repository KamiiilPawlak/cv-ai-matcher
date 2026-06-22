# Witamy w dokumentacji CV AI Matcher

**CV AI Matcher** to inteligentny system automatyzujący proces analizy, ekstrakcji oraz dopasowywania dokumentów aplikacyjnych (CV) do wymagań ofert pracy przy użyciu modeli językowych (LLM) oraz hybrydowego potoku OCR.

---

## 🚀 Główne Funkcjonalności

- **Hybrydowa Ekstrakcja Tekstu (OCR):** Przetwarzanie plików PDF (zarówno interaktywnych, jak i skanów) przy użyciu narzędzi `pdfplumber` oraz `Tesseract OCR`.
- **Czyszczenie i Normalizacja Danych:** Automatyczne usuwanie szumów tekstowych, walidacja rozmiarów plików oraz normalizacja struktury danych wejściowych.
- **Moduł Backendowy:** Wydajne, asynchroniczne API zbudowane w oparciu o framework FastAPI oraz bazę danych PostgreSQL.

---

## 🏗️ Architektura Systemu

Projekt został zaprojektowany z myślą o czystej architekturze (Clean Architecture) oraz modułowości (Package-by-Layer):

```bash
CV-AI-MATCHER/
├── .github/                            # Konfiguracja GitHub (np. Workflows do CI/CD, szablony Pull Requestów)
├── .vscode/                            # Lokalne ustawienia edytora VS Code (np. konfiguracja debuggera, ruff)
├── backend/                            # Główny katalog aplikacji backendowej (FastAPI)
│   ├── .venv/                          # Lokalne środowisko wirtualne Pythona (izolacja zależności)
│   ├── app/                            # Kod źródłowy aplikacji backendowej
│   │   ├── __pycache__/                # Skompilowane pliki bytecode Pythona (.pyc)
│   │   ├── api/                        # Warstwa komunikacji HTTP (Routing i Endpointy)
│   │   │   └── v1/                     # Wersjonowanie API (v1)
│   │   │       ├── routes/             # Definicje konkretnych ścieżek/kontrolerów
│   │   │       │   ├── __init__.py
│   │   │       │   ├── health.py       # Endpoint sprawdzający status działania aplikacji (Healthcheck)
│   │   │       │   └── ingestion.py    # Endpointy odpowiedzialne za przyjmowanie dokumentów CV
│   │   │       ├── __init__.py
│   │   │       └── router.py           # Główny agregator ścieżek dla wersji v1
│   │   ├── core/                       # Globalna konfiguracja i ustawienia systemowe
│   │   │   ├── config.py               # Mapowanie zmiennych środowiskowych (.env) i ustawienia Pydantic
│   │   │   ├── logger.py               # Konfiguracja logowania zdarzeń (logów) aplikacji
│   │   │   └── security.py             # Mechanizmy bezpieczeństwa (np. haszowanie, weryfikacja plików, tokeny)
│   │   ├── crud/                       # Warstwa bezpośredniego dostępu do bazy danych (Create, Read, Update, Delete)
│   │   │   ├── __init__.py
│   │   │   ├── datalake_cv.py          # Operacje bazodanowe powiązane z zapisanymi dokumentami CV
│   │   │   └── datalake_scraper.py     # Operacje bazodanowe dedykowane danym ze scrapera
│   │   ├── db/                         # Konfiguracja połączenia z bazą danych
│   │   │   ├── __init__.py
│   │   │   └── database.py             # Inicjalizacja silnika bazy (Engine) i sesji (SQLModel/SQLAlchemy)
│   │   ├── models/                     # Modele bazodanowe (definicje tabel w bazie danych)
│   │   │   ├── __init__.py
│   │   │   ├── cv.py                   # Model reprezentujący strukturę tabeli CV w bazie
│   │   │   └── scraper.py              # Model dla danych pozyskanych ze scrapera
│   │   ├── schema/                     # DTO (Data Transfer Objects) – walidacja danych wejściowych/wyjściowych
│   │   │   ├── ingestion_dto.py        # Schematy Pydantic do walidacji przesyłanych plików/metadanych
│   │   │   └── scraper_dto.py          # Schematy Pydantic dla danych wejściowych ze scrapera
│   │   ├── services/                   # Warstwa logiki biznesowej (serce systemu)
│   │   │   ├── etl_cv_service/         # Serwis odpowiedzialny za potok przetwarzania danych CV
│   │   │   │   ├── transformers/       # Komponenty odpowiedzialne za transformację tekstu
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── cleaning.py     # Czyszczenie tekstu z OCR (usuwanie szumów, regex)
│   │   │   │   │   └── normalization.py# Standaryzacja i normalizacja danych (np. formaty dat, Unicode)
│   │   │   │   ├── __init__.py
│   │   │   │   └── pipeline.py         # Koordynator całego procesu ETL (Extract, Transform, Load)
│   │   │   ├── ingestion_service/      # Serwis obsługujący przyjmowanie i wstępne przetwarzanie dokumentów
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file_service.py     # Walidacja plików (rozmiar, magic bytes) oraz zapis na dysku/chmurze
│   │   │   │   ├── ingestion_service.py# Główna logika orkiestracji procesu przyjęcia dokumentu
│   │   │   │   └── ocr_service.py      # Silnik OCR (np. Tesseract/pdfplumber) do ekstrakcji surowego tekstu
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── main.py                     # Punkt wejściowy aplikacji FastAPI (inicjalizacja i uruchomienie serwera)
│   ├── logs/                           # Przechowywane pliki logów generowane przez aplikację
│   ├── tests/                          # Testy automatyczne (jednostkowe i integracyjne backendu)
│   ├── uploads/                        # Lokalny katalog tymczasowy na wgrywane pliki (np. dokumenty CV do OCR)
│   ├── .env                            # Lokalne zmienne środowiskowe (nie powinno trafiać do Gita!)
│   ├── .env.test                       # Zmienne środowiskowe dedykowane dla środowiska testowego
│   ├── Dockerfile                      # Instrukcja budowania obrazu Dockerowego dla aplikacji backendowej
│   ├── pyproject.toml                  # Konfiguracja zależności (Poetry/Pipenv) oraz lintera i formatowania (Ruff)
│   └── pytest.ini                      # Konfiguracja frameworka testowego pytest
├── docs/                               # Dokumentacja projektu (zgodnie ze strukturą Diátaxis)
│   ├── architecture/                   # Opisy decyzji architektonicznych i diagramy przepływu danych
│   ├── how-to/                         # Praktyczne poradniki krok-po-kroku dla deweloperów
│   │   ├── local_development.md        # Instrukcja konfiguracji i uruchomienia środowiska lokalnego
│   │   └── testing.md                  # Instrukcja uruchamiania i pisania testów automatycznych
│   ├── reference/                      # Dokumentacja techniczna kodu, API i modułów
│   └── index.md                        # Strona główna dokumentacji
├── frontend/                           # Kod źródłowy aplikacji klienckiej (np. React + TypeScript / Zustand)
├── scripts/                            # Pomocnicze skrypty automatyzujące powtarzalne zadania
│   ├── run.ps1                         # Skrypt automatyzujący uruchamianie projektu (PowerShell dla Windows)
│   └── run.sh                          # Skrypt automatyzujący uruchamianie projektu (Bash dla Linux/macOS)
├── .dockerignore                       # Pliki i katalogi ignorowane przy budowaniu obrazów Dockera (przyspiesza build)
├── .gitattributes                      # Konfiguracja atrybutów Gita (np. ujednolicenie końców linii LF/CRLF)
├── .gitignore                          # Pliki i foldery ignorowane przez system kontroli wersji Git (np. .venv, .env)
├── .pre-commit-config.yaml             # Konfiguracja hooków uruchamianych przed każdym commitem (linter, formatowanie)
├── commitlint.config.js                # Konfiguracja wymuszania standaryzacji komunikatów commitów (Conventional Commits)
├── docker-compose.yml                  # Definicja wielokontenerowego środowiska (np. backend + baza danych)
├── Dockerfile.docs                     # Kontener dedykowany do budowania i serwowania dokumentacji MkDocs
├── LICENSE                             # Licencja oprogramowania projektu
├── mkdocs.yml                          # Główny plik konfiguracyjny narzędzia MkDocs do generowania dokumentacji
└── README.md                           # Główny opis projektu, instrukcja instalacji i podstawowe informacje

```

---

## 🗺️ Szybki Start & Nawigacja

Aby szybko zacząć pracę z projektem, przejdź do odpowiednich sekcji dokumentacji:

Instrukcja Instalacji: Dowiedz się, jak krok po kroku uruchomić całe środowisko wraz z bazą danych i backendem przy użyciu jednego polecenia Docker.

Dokumentacja API (Swagger): Po uruchomieniu projektu w Dockerze pełna, interaktywna specyfikacja endpointów jest dostępna pod adresem http://localhost:8000/docs.
