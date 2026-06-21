# Moduł Ingestion Service

Moduł odpowiada za orkiestrację procesu przyjmowania dokumentów aplikacyjnych, wstępną walidację plików na poziomie binarnym oraz ekstrakcję surowego tekstu za pomocą technologii OCR.

---

## 1. Ingestion Service (Główna Logika)

`app.services.ingestion_service.ingestion_service`
::: app.services.ingestion_service.ingestion_service

Główny punkt wejściowy (orkiestrator) dla potoku przetwarzania dokumentów.

- **Zadania:**
  - Przyjmowanie obiektów przesyłanych przez API.
  - Koordynacja przepływu danych między walidacją pliku a silnikiem OCR.
  - Przekazywanie wyekstrahowanego tekstu dalej do potoku ETL.

---

## 2. File Service (Zarządzanie Plikami)

`app.services.ingestion_service.file_service`

Komponent odpowiedzialny za niskopoziomowe operacje na plikach oraz bezpieczeństwo systemu przed złośliwym oprogramowaniem.

- **Zadania:**
  - **Weryfikacja formatów:** Sprawdzanie rozszerzeń plików.
  - **Bezpieczeństwo (Magic Bytes):** Analiza sygnatury binarnej plików (np. czy plik `.pdf` rzeczywiście zaczyna się od bajtów `%PDF`), zapobiegająca próbom oszukania systemu przez zmianę samego rozszerzenia pliku wykonywalnego.

---

## 3. OCR Service (Ekstrakcja Tekstu)

`app.services.ingestion_service.ocr_service`
::: app.services.ingestion_service.ocr_service

Warstwa integracji z zewnętrznym silnikiem optycznego rozpoznawania znaków (OCR).

- **Zadania:**
  - Wykrywanie warstwy tekstowej w dokumentach cyfrowych.
  - Przetwarzanie skanów oraz plików graficznych przy użyciu biblioteki **Tesseract OCR**.
  - Zwracanie surowego ciągu znaków (raw text) do dalszej obróbki.
