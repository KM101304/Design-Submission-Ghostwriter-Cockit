from app.services.storage import LocalStorageClient, safe_filename


def test_safe_filename_rewrites_unsafe_chars() -> None:
    assert safe_filename("my file?.pdf") == "my_file_.pdf"


def test_local_storage_put_bytes(tmp_path) -> None:
    client = LocalStorageClient(root=str(tmp_path))
    key = client.put_bytes("submissions/demo/doc.txt", b"hello", "text/plain")
    assert key == "submissions/demo/doc.txt"
    assert (tmp_path / "submissions/demo/doc.txt").read_bytes() == b"hello"
