from typing import MutableSequence, Sequence
from unittest import TestCase

from ..std2.collections import defaultlist

_SMS = Sequence[MutableSequence[str]]


class DefaultList(TestCase):
    def test_1(self) -> None:
        l2: Sequence[str] = []
        ls: _SMS = (defaultlist(lambda: ""), [])
        for l1 in ls:
            self.assertEqual(len(l1), 0)
            with self.assertRaises(IndexError):
                l1[1]
            with self.assertRaises(IndexError):
                l1[-1]
            self.assertEqual(l1[:], l2)

    def test_2(self) -> None:
        ls: _SMS = (defaultlist(lambda: ""), [])
        l2 = ["a"]
        for l1 in ls:
            l1.append("a")
            self.assertEqual(len(l1), 1)
            with self.assertRaises(IndexError):
                l1[1]
            with self.assertRaises(IndexError):
                l1[-2]
            self.assertEqual(l1[0], "a")
            self.assertEqual(l1[-1], "a")
            self.assertEqual(l1[:], l2)

    def test_3(self) -> None:
        ls: _SMS = (defaultlist(lambda: ""), [])
        l2 = ["a"]
        for l1 in ls:
            l1.insert(2, "a")
            self.assertEqual(len(l1), 1)
            with self.assertRaises(IndexError):
                l1[1]
            with self.assertRaises(IndexError):
                l1[-2]
            self.assertEqual(l1[:], l2)

    def test_4(self) -> None:
        ls: _SMS = (defaultlist(lambda: ""), [])
        l2 = ["b", "d", "c", "a"]
        for l1 in ls:
            l1.insert(2, "a")
            l1.insert(0, "b")
            l1.insert(-1, "c")
            l1.insert(1, "d")
            self.assertEqual(len(l1), len(l2))
            self.assertEqual(l1[:], l2)

    def test_5(self) -> None:
        for l in (tuple(), ("e", "d"), ("e", "d", "f"), ("e", "d", "f", "g")):
            l0 = defaultlist(lambda: "")
            l0[:] = l
            ls = [l0, []]
            l2 = ["a", "b", "c"]
            for l1 in ls:
                l1[:] = ["a", "b", "c"]
                self.assertEqual(len(l1), len(l2))
                self.assertEqual(l1[:], l2)

    def test_6(self) -> None:
        for (i, j, k), l in (
            ((0, 0, None), ()),
            ((0, 0, None), ("e", "d")),
            ((0, 0, None), ("e", "d", "f")),
            ((0, 0, None), ("e", "d", "f", "g")),
        ):
            l0 = defaultlist(lambda: "")
            l0[i:j:k] = l
            ls = [l0, []]
            l2 = ["a", "b", "c"]
            for l1 in ls:
                l1[:] = ["a", "b", "c"]
                self.assertEqual(len(l1), len(l2))
                self.assertEqual(l1[:], l2)
