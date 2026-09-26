#!/usr/bin/env python3
"""M8.2 — compare a recall-suite record with KNOWN_DEFECTS.md's "once fixed" column.

usage: python3 gen/check_known_fixed.py results/known-<commit>.txt [--fixed DEF-99 DEF-102 ...]

The record is gen/run_known.py's output. For each defect named by --fixed (the
fixes the compiler carries), every one of its rows must match the column; a
defect not named is reported but not judged. The column is transcribed below
from KNOWN_DEFECTS.md: (npkc rc, the codes, -O0, -O2), where "-" means the
program was not built. A refusal row matches when npkc exits 1 and its codes
are exactly the stated set.
"""
import argparse, re

ONCE_FIXED = {
    "def99_fixed_move/case1_element_move": ("DEF-99", 1, ["NITPICK-TYPE-084"], "-", "-"),
    "def99_fixed_move/case2_element_pass": ("DEF-99", 1, ["NITPICK-TYPE-084"], "-", "-"),
    "def99_fixed_move/case3_scalar_move": ("DEF-99", 1, ["NITPICK-TYPE-084"], "-", "-"),
    "def99_fixed_move/case4_clone_control": ("DEF-99", 0, [], "0", "0"),
    "def102_lent_param/lent_field": ("DEF-102", 1, ["NITPICK-TYPE-085"], "-", "-"),
    "def102_lent_param/lent_field_nodread": ("DEF-102", 1, ["NITPICK-TYPE-085"], "-", "-"),
    "def102_lent_param/ctl_local": ("DEF-102", 0, [], "22", "22"),
    "def102_lent_param/ctl_whole_lent_string": ("DEF-102", 1, ["NITPICK-TYPE-085"], "-", "-"),
    "def102_lent_param/ctl_move_param": ("DEF-102", 0, [], "0", "0"),
    "def104_generic_lent/gen_id": ("DEF-104", 1, ["NITPICK-TYPE-047"], "-", "-"),
    "def104_generic_lent/gen_id_read": ("DEF-104", 1, ["NITPICK-TYPE-047"], "-", "-"),
    "def104_generic_lent/ctl_concrete": ("DEF-104", 1, ["NITPICK-TYPE-047"], "-", "-"),
    "def105_import_scope/case1_table_only": ("DEF-105", 0, [], "0", "0"),
    "def105_import_scope/case2_same_name": ("DEF-105", 0, [], "0", "0"),
    "def105_import_scope/case3_wider_same_name": ("DEF-105", 0, [], "0", "0"),
    "def105_import_scope/case4_type_imported": ("DEF-105", 0, [], "0", "0"),
    "def105_import_scope/case5_type_imported_same_name": ("DEF-105", 1, ["NITPICK-RESOLVE-001"], "-", "-"),
    "def105_import_scope/case6_scalar_same_name": ("DEF-105", 0, [], "0", "0"),
    "def105_import_scope/case7_function_only": ("DEF-105", 0, [], "0", "0"),
}
LINE = re.compile(r"^(\S+)\s+npkc=(\S+) \[([^\]]*)\]\s+O0=(\S+)\s+O2=(\S+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("record")
    ap.add_argument("--fixed", nargs="*", default=[])
    a = ap.parse_args()
    seen, bad, judged = set(), 0, 0
    for l in open(a.record):
        m = LINE.match(l)
        if not m:
            continue
        name, rc, codes, o0, o2 = m.groups()
        seen.add(name)
        if name not in ONCE_FIXED:
            print("NOT IN THE TABLE  %s" % l.rstrip())
            bad += 1
            continue
        d, erc, ecodes, eo0, eo2 = ONCE_FIXED[name]
        got = (rc, sorted(c for c in codes.split(",") if c), o0, o2)
        want = (str(erc), sorted(ecodes), eo0, eo2)
        if d not in a.fixed:
            print("not judged (%s's fix not named)  %s" % (d, name))
            continue
        judged += 1
        ok = got == want
        bad += not ok
        print("%-8s %-7s %-50s got npkc=%s [%s] %s/%s%s" % (
            "match" if ok else "MISMATCH", d, name, rc, codes, o0, o2,
            "" if ok else "   want npkc=%s [%s] %s/%s" % (want[0], ",".join(want[1]), eo0, eo2)))
    for name in sorted(set(ONCE_FIXED) - seen):
        print("MISSING FROM THE RECORD  %s" % name)
        bad += 1
    print("%d rows judged, %d mismatches or gaps" % (judged, bad))


if __name__ == "__main__":
    main()
