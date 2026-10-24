"""validate_artifact 最小测试矩阵（十九轮 gate P2）：
十八轮 P1 修复（解析级校验 + 压缩层剥离）此前零测试钉扎，可静默退化。
矩阵：5 格式 × {有效, 损坏} + 压缩变体 + 未知扩展名unchecked语义。
"""
import gzip
import os
import pytest

from tbtools_cli.executor import validate_artifact


@pytest.fixture()
def tmpd(tmp_path):
    return str(tmp_path)


def _w(path: str, content: str, compress: bool = False) -> str:
    if compress or path.endswith(".gz"):
        with gzip.open(path, "wt", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return path


class TestValidateArtifactMatrix:
    """格式 × 样本 有效性矩阵"""

    # --- FASTA ---
    def test_fasta_valid(self, tmpd):
        p = _w(os.path.join(tmpd, "ok.fa"), ">seq1\nACGT\n>seq2\nTTTT\n")
        ok, msg = validate_artifact(p)
        assert ok and "fasta" in msg

    def test_fasta_broken(self, tmpd):
        p = _w(os.path.join(tmpd, "bad.fa"), "garbage no header at all")
        ok, msg = validate_artifact(p)
        assert not ok

    def test_fasta_gz_valid(self, tmpd):
        p = _w(os.path.join(tmpd, "ok.fa.gz"), ">seq1\nACGT\n>seq2\nTTTT\n")
        ok, msg = validate_artifact(p)
        assert ok and "fasta" in msg

    def test_fasta_gz_broken(self, tmpd):
        """十八轮 arch P1 回归钉扎: bad.fa.gz 不得绕过校验"""
        p = _w(os.path.join(tmpd, "bad.fa.gz"), "garbage no header")
        ok, msg = validate_artifact(p)
        assert not ok

    # --- Newick ---
    def test_newick_valid(self, tmpd):
        p = _w(os.path.join(tmpd, "ok.nwk"), "((A:1,B:1):1,(C:1,D:1):1);\n")
        ok, msg = validate_artifact(p)
        assert ok

    def test_newick_broken(self, tmpd):
        p = _w(os.path.join(tmpd, "bad.nwk"), "((A,B;")  # 括号不平衡
        ok, msg = validate_artifact(p)
        assert not ok

    # --- GFF ---
    def test_gff_valid(self, tmpd):
        p = _w(os.path.join(tmpd, "ok.gff3"),
               "##gff-version 3\nchr1\tsrc\tgene\t1\t100\t.\t+\t.\tID=g1\n")
        ok, msg = validate_artifact(p)
        assert ok

    def test_gff_broken(self, tmpd):
        p = _w(os.path.join(tmpd, "bad.gff3"), "random text with no gff markers\n")
        ok, msg = validate_artifact(p)
        assert not ok

    # --- TSV ---
    def test_tsv_valid(self, tmpd):
        p = _w(os.path.join(tmpd, "ok.tsv"), "a\tb\tc\n1\t2\t3\n")
        ok, msg = validate_artifact(p)
        assert ok

    def test_tsv_empty(self, tmpd):
        p = _w(os.path.join(tmpd, "empty.tsv"), "\n\n\n")
        ok, msg = validate_artifact(p)
        assert not ok

    # --- SVG ---
    def test_svg_valid(self, tmpd):
        p = _w(os.path.join(tmpd, "ok.svg"), '<?xml version="1.0"?><svg xmlns="..."><rect/></svg>')
        ok, msg = validate_artifact(p)
        assert ok

    def test_svg_broken(self, tmpd):
        p = _w(os.path.join(tmpd, "bad.svg"), "not xml at all")
        ok, msg = validate_artifact(p)
        assert not ok

    # --- 缺失文件 ---
    def test_missing_file(self, tmpd):
        ok, msg = validate_artifact(os.path.join(tmpd, "nonexistent.fa"))
        assert not ok and "missing" in msg

    # --- 未知扩展名: 谎报修复后的语义 ---
    def test_unknown_ext_reports_unchecked(self, tmpd):
        """十九轮 gate P2: exists(ext, no parser) 不得谎报为通过——消息应含 unchecked 语义"""
        p = _w(os.path.join(tmpd, "data.xyz123"), "whatever\n")
        ok, msg = validate_artifact(p)
        assert ok  # 不阻断(无解析器不怪文件)
        assert "unchecked" in msg or "no parser" in msg, f"未知扩展名消息未标 unchecked: {msg}"
