import os
import zipfile
import pytest
from prop.s3io import is_s3, download_to_tmp, list_from_zip


def test_is_s3():
    assert is_s3('s3://bucket/key/file.txt')
    assert not is_s3('http://example.com')
    assert not is_s3('/local/path')
    assert not is_s3('s3:/broken')


def test_download_local(tmp_path):
    f = tmp_path / 'sample.txt'
    f.write_text('hello')
    got = download_to_tmp(str(f))
    assert os.path.isfile(got)
    assert open(got).read() == 'hello'


def test_list_from_zip(tmp_path):
    # create zip
    zf = tmp_path / 't.zip'
    d1 = tmp_path / 'dir'
    d1.mkdir()
    (d1 / 'a.txt').write_text('A')
    (d1 / 'b.txt').write_text('B')
    with zipfile.ZipFile(zf, 'w') as z:
        z.write(d1 / 'a.txt', arcname='a.txt')
        z.write(d1 / 'b.txt', arcname='nested/b.txt')
    files = list_from_zip(str(zf))
    assert len(files) == 2
    contents = sorted([open(p).read() for p in files])
    assert contents == ['A', 'B']


@pytest.mark.skipif('AWS_ACCESS_KEY_ID' not in os.environ, reason='No AWS creds for live s3 test')
def test_download_s3_live():  # pragma: no cover
    # Provide bucket/key via env for optional live test
    uri = os.environ.get('TEST_S3_URI')
    if not uri:
        pytest.skip('TEST_S3_URI not set')
    path = download_to_tmp(uri)
    assert os.path.isfile(path)
    assert os.path.getsize(path) > 0
