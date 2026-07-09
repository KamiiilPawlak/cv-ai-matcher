from app.services.etl_cv_service.transformers.cleaning import clean_ocr_text


def test_clean_ocr_empty_inputs():
    # Checks for a completely empty string
    assert clean_ocr_text("") == ""

    # Checks a string consisting of spaces
    assert clean_ocr_text("   ") == ""
