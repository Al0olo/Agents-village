from collections import Counter

import pytest

from agent_village.facts import CELLS, TEMPLATES, Fact, Level, design, generate, utility_facts

BLOCKS = range(20)


def cell(fact):
    return (fact.plausibility, fact.status)


def test_a_block_has_six_false_and_four_true_facts():
    facts = generate(1, 0)
    assert len(facts) == 10
    assert sum(not f.truth for f in facts) == 6
    assert sum(f.truth for f in facts) == 4
    assert len({f.id for f in facts}) == 10


@pytest.mark.parametrize("block", BLOCKS)
def test_true_facts_cover_every_plausibility_and_status_cell_once(block):
    true = [cell(f) for f in generate(1, block) if f.truth]
    assert sorted(true) == sorted(CELLS)


@pytest.mark.parametrize("block", BLOCKS)
def test_false_facts_cover_every_cell_and_two_cells_twice(block):
    counts = Counter(cell(f) for f in generate(1, block) if not f.truth)
    assert set(counts) == set(CELLS)
    assert sorted(counts.values()) == [1, 1, 2, 2]


def test_the_doubled_false_cells_rotate_so_four_blocks_balance_every_cell():
    totals = Counter()
    for block in range(4):
        totals.update(cell(f) for f in generate(1, block) if not f.truth)
    assert set(totals.values()) == {6}


def test_twenty_blocks_balance_truth_plausibility_and_status():
    false, true = Counter(), Counter()
    for block in BLOCKS:
        for f in generate(1, block):
            (true if f.truth else false)[cell(f)] += 1
    assert set(false.values()) == {30} and set(true.values()) == {20}


def test_ten_blocks_put_every_template_in_every_truth_position_equally():
    by_template = Counter()
    for block in range(10):
        for f in generate(1, block):
            by_template[(f.template, f.truth)] += 1
    assert {n for (_, truth), n in by_template.items() if truth} == {4}
    assert {n for (_, truth), n in by_template.items() if not truth} == {6}


def test_the_design_is_the_source_of_the_assignment():
    for block in (0, 3, 7):
        assigned = [(f.truth, f.plausibility, f.status) for f in generate(1, block)]
        expected = [design(block)[(i + block) % 10] for i in range(10)]
        assert assigned == expected


def test_generation_is_deterministic_and_depends_on_seed_and_block():
    assert generate(1, 2) == generate(1, 2)
    assert generate(1, 2) != generate(2, 2)
    assert generate(1, 2) != generate(1, 3)


def test_entities_are_distinct_within_a_block():
    for block in BLOCKS:
        entities = [f.entity for f in generate(3, block)]
        assert len(set(entities)) == len(entities)


def test_each_fact_is_built_from_its_template():
    for fact in generate(5, 1):
        template = next(t for t in TEMPLATES if t.key == fact.template)
        pool = template.plausible if fact.plausibility is Level.HIGH else template.implausible
        assert fact.answer in pool
        assert fact.text == template.statement.format(entity=fact.entity, value=fact.answer)
        assert fact.observation == template.observation.format(
            entity=fact.entity, value=fact.answer
        )
        assert fact.question == template.question.format(entity=fact.entity)


def test_the_question_never_contains_the_answer():
    for block in BLOCKS:
        for fact in generate(7, block):
            assert fact.answer.lower() not in fact.question.lower()
            assert fact.entity in fact.question


def test_plausible_and_implausible_values_do_not_overlap_in_any_template():
    for template in TEMPLATES:
        assert not set(template.plausible) & set(template.implausible)
        assert len(template.plausible) >= 3 and len(template.implausible) >= 3


def test_templates_are_ten_distinct_attributes_with_filled_placeholders():
    assert len({t.key for t in TEMPLATES}) == len(TEMPLATES) == 10
    for t in TEMPLATES:
        assert "{entity}" in t.statement and "{value}" in t.statement
        assert "{entity}" in t.observation and "{value}" in t.observation
        assert "{entity}" in t.question and "{value}" not in t.question


@pytest.mark.parametrize(
    "word", ["false", "untrue", "rumour", "rumor", "claim", "supposed", "not "]
)
def test_wording_does_not_give_the_truth_label_away(word):
    for block in range(4):
        for fact in generate(1, block):
            for text in (fact.text, fact.observation, fact.question):
                assert word not in text.lower()


def test_every_fact_is_a_frozen_value():
    fact = generate(1, 0)[0]
    assert isinstance(fact, Fact)
    with pytest.raises(AttributeError):
        fact.truth = not fact.truth


@pytest.mark.parametrize("block", [-1])
def test_a_negative_block_is_rejected(block):
    with pytest.raises(ValueError):
        generate(1, block)


def test_different_blocks_of_one_seed_get_different_names_and_values():
    entities = {f.entity for block in range(10) for f in generate(1, block)}
    assert len(entities) > 40
    first, second = generate(1, 0), generate(1, 1)
    assert {f.entity for f in first} != {f.entity for f in second}
    assert [f.answer for f in first] != [f.answer for f in second]


def test_a_block_has_two_true_utility_facts_one_for_each_status():
    facts = utility_facts(1, 0)
    assert [f.id for f in facts] == ["u1", "u2"]
    assert all(f.truth and f.utility and f.plausibility is Level.HIGH for f in facts)
    assert [f.status for f in facts] == [Level.HIGH, Level.LOW]
    assert not any(f.utility for f in generate(1, 0))


@pytest.mark.parametrize("block", BLOCKS)
def test_utility_facts_are_about_other_entities_than_the_blocks_ten(block):
    entities = [f.entity for f in generate(3, block) + utility_facts(3, block)]
    assert len(set(entities)) == 12


def test_utility_facts_are_built_from_their_template_and_rotate_over_blocks():
    seen = set()
    for block in range(5):
        for fact in utility_facts(2, block):
            template = next(t for t in TEMPLATES if t.key == fact.template)
            assert fact.answer in template.plausible
            assert fact.text == template.statement.format(entity=fact.entity, value=fact.answer)
            assert fact.observation == template.observation.format(
                entity=fact.entity, value=fact.answer
            )
            assert fact.question == template.question.format(entity=fact.entity)
            seen.add(fact.template)
    assert seen == {t.key for t in TEMPLATES}


def test_utility_generation_is_deterministic_and_depends_on_seed_and_block():
    assert utility_facts(1, 2) == utility_facts(1, 2)
    assert utility_facts(1, 2) != utility_facts(2, 2)
    assert utility_facts(1, 2) != utility_facts(1, 3)


def test_the_blocks_ten_facts_do_not_change_when_utility_facts_exist():
    before = generate(1, 4)
    utility_facts(1, 4)
    assert generate(1, 4) == before


def test_utility_wording_does_not_give_the_truth_label_away():
    for block in range(4):
        for fact in utility_facts(1, block):
            for text in (fact.text, fact.observation, fact.question):
                for word in ("false", "untrue", "rumour", "claim", "supposed", "not "):
                    assert word not in text.lower()
            assert fact.answer.lower() not in fact.question.lower()


def test_a_negative_block_is_rejected_for_utility_facts_too():
    with pytest.raises(ValueError):
        utility_facts(1, -1)
