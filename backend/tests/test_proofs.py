from engine.proofs.pumping import check_all, decompositions, validate_choice
from engine.proofs.templates import get_template, list_templates


def test_decomposition_count_and_anbn_witness():
    template = get_template("anbn")
    witness = template.witness(3)
    assert len(decompositions(witness, 3)) == 6
    report = check_all(template, witness, 3)
    assert report.total == 6
    assert not report.survivors


def test_regular_demo_can_have_survivors():
    report = check_all(get_template("abstar"), "ababab", 3)
    assert report.survivors
    assert "proves nothing" in report.steps[-1].description


def test_all_templates_membership_examples():
    for template in list_templates():
        assert template.membership(template.witness(3))
    assert get_template("prime").membership("aaaaaaa")
    assert not get_template("prime").membership("aaaa")
    assert get_template("balanced").membership("(()())")
    assert not get_template("balanced").membership("(()")


def test_validate_choice_reports_problems():
    problems = validate_choice(get_template("anbn"), 3, "ab")
    assert any("length at least" in problem for problem in problems)
