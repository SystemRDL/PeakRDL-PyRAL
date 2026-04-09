from pyral_testutils.pyral_testcase import PyRALTestcase
from peakrdl_pyral_runtime import model as pyral
from peakrdl_pyral.name_filter import GROUP_RESERVED_WORDS, REGISTER_RESERVED_WORDS

class TestNameFilter(PyRALTestcase):
    def test_reserved_words_complete(self) -> None:
        self.export([
            "rdl_src/tiny.rdl"
        ])
        import tiny
        ral_group: pyral.RALGroup = tiny.get_ral()
        ral_reg: pyral.RALRegister = ral_group.r0

        group_reserved_words = set()
        for word in ral_group.__dir__():
            if word.startswith("__") and word.endswith("__"):
                continue
            group_reserved_words.add(word)

        reg_reserved_words = set()
        for word in ral_reg.__dir__():
            if word.startswith("__") and word.endswith("__"):
                continue
            reg_reserved_words.add(word)

        self.assertSetEqual(group_reserved_words, GROUP_RESERVED_WORDS)
        self.assertSetEqual(reg_reserved_words, REGISTER_RESERVED_WORDS)
