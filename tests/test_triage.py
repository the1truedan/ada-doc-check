from pathlib import Path

from ada_check.triage import looks_like_binary, needs_ocr, process_paths


def test_looks_like_binary_jfif():
    # JFIF-like header as "text"
    blob = "\xff\xd8\xff\xe0\x00\x10JFIF" + ("\x00" * 100)
    assert looks_like_binary(blob) is True


def test_missing_file_undecidable(tmp_path: Path):
    missing = tmp_path / "nope.pdf"
    r = needs_ocr(missing)
    assert r["decidable"] is False
    assert r["reason"] == "file not found"
    assert r["needs_ocr"] is None


def test_good_text_file(tmp_path: Path):
    p = tmp_path / "doc.txt"
    p.write_text("Accessible paragraph. " * 20, encoding="utf-8")
    r = needs_ocr(p, min_chars=50)
    assert r["decidable"] is True
    assert r["needs_ocr"] is False
    assert r["accessible_as_is"] is True


def test_short_text_needs_ocr(tmp_path: Path):
    p = tmp_path / "short.txt"
    p.write_text("hi", encoding="utf-8")
    r = needs_ocr(p, min_chars=50)
    assert r["decidable"] is True
    assert r["needs_ocr"] is True


def test_binary_image_not_accessible(tmp_path: Path):
    p = tmp_path / "scan.jpg"
    # minimal JPEG SOI + JFIF marker bytes
    p.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 200)
    r = needs_ocr(p)
    assert r["accessible_as_is"] is False
    assert r["needs_ocr"] is True
    # either undecidable binary or needs_ocr true
    assert r["decidable"] is False or r["needs_ocr"] is True


def test_process_paths_batch(tmp_path: Path):
    good = tmp_path / "a.txt"
    good.write_text("word " * 100, encoding="utf-8")
    missing = tmp_path / "gone.txt"
    report = process_paths([good, missing], min_chars=20)
    assert report["considered"] == 2
    assert report["accessible_as_is"] == 1
    assert report["undecidable"] == 1
