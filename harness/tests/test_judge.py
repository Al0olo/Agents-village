import csv
import dataclasses
import io
import itertools
import random
import re
from collections import Counter

import pytest
from villages import NAMES, gossip

from agent_village.arms import BASE
from agent_village.eventlog import EventLog
from agent_village.facts import generate
from agent_village.fork import build
from agent_village.judge import (
    AWARENESS_RUBRIC,
    FACT_RUBRIC,
    Blinded,
    Item,
    Record,
    agreement,
    attach,
    blind,
    code_items,
    collect,
    parse_code,
    read_sheet,
    sample_sheet,
)
from agent_village.model import FakeBackend, ModelError, RecordedBackend, Response
from agent_village.planting import Roster, make_plan, plant
from agent_village.probes import AWARENESS_QUESTION
from agent_village.runner import Spec

SPECS = [Spec(n, "fake/model") for n in NAMES]
FACTS = generate(1, 0)
ROSTER = Roster(NAMES, ("ada", "bo"))
PLAN = make_plan(FACTS, ROSTER, 1, 0)


def planted_log(tmp_path, name, answers=None):
    """A planted village with a hand-written probe for every citizen and question."""
    world = build(
        EventLog(tmp_path / name),
        random.Random(1),
        FakeBackend(gossip),
        BASE.policy,
        BASE.prompt,
        SPECS,
        3,
    )
    plant(world, PLAN)
    answers = answers or {}
    for citizen in NAMES:
        for fact in FACTS:
            reply = answers.get((citizen, fact.id), f"About {fact.answer}.")
            world.log.append(
                "probe",
                citizen,
                {
                    "kind": "fact",
                    "key": fact.id,
                    "question": fact.question,
                    "reply": reply,
                    "answer": reply,
                },
            )
        world.log.append(
            "probe",
            citizen,
            {
                "kind": "awareness",
                "key": "awareness",
                "question": AWARENESS_QUESTION,
                "reply": "Nothing odd.",
                "answer": "Nothing odd.",
            },
        )
    return world.log


@pytest.fixture
def logs(tmp_path):
    return {
        (0, "A"): planted_log(tmp_path, "a.jsonl"),
        (0, "D"): planted_log(tmp_path, "d.jsonl"),
        (1, "A"): planted_log(tmp_path, "a1.jsonl"),
    }


class Spy:
    def __init__(self, reply='{"code": "asserts"}'):
        self.reply, self.requests = reply, []

    def complete(self, request):
        self.requests.append(request)
        text = self.reply(request) if callable(self.reply) else self.reply
        return Response(text, request.model, "fake", 1, 1)


def test_collect_reads_every_probe_with_its_planted_fact(logs):
    records = collect(logs)
    assert len(records) == 3 * 8 * 11
    fact_records = [r for r in records if r.kind == "fact"]
    assert len(fact_records) == 3 * 8 * 10
    one = next(r for r in fact_records if r.key == FACTS[0].id and r.citizen == "cy")
    assert (one.block, one.arm) in {(0, "A"), (0, "D"), (1, "A")}
    assert one.question == FACTS[0].question
    assert one.claim == FACTS[0].text
    assert one.truth is FACTS[0].truth
    assert one.holders == next(p.holders for p in PLAN.plantings if p.fact.id == FACTS[0].id)
    awareness = [r for r in records if r.kind == "awareness"]
    assert len(awareness) == 3 * 8
    assert all(r.claim == "" and r.truth is None and r.holders == () for r in awareness)


def test_collect_is_ordered_by_block_and_arm(logs):
    records = collect(dict(reversed(list(logs.items()))))
    keys = [(r.block, r.arm) for r in records]
    assert keys == sorted(keys)


def test_a_probe_about_a_fact_that_was_not_planted_is_an_error(tmp_path):
    log = planted_log(tmp_path, "x.jsonl")
    log.append(
        "probe", "ada", {"kind": "fact", "key": "f99", "question": "q", "reply": "r", "answer": "r"}
    )
    with pytest.raises(ValueError, match="f99"):
        collect({(0, "A"): log})


def test_items_carry_only_what_a_judge_may_see(logs):
    blinded = blind(collect(logs), 1)
    assert [f.name for f in dataclasses.fields(Item)] == [
        "item_id",
        "kind",
        "question",
        "claim",
        "answer",
    ]
    assert isinstance(blinded, Blinded)
    assert len(blinded.items) == len(blinded.key) == len(collect(logs))
    for item in blinded.items:
        record = blinded.key[item.item_id]
        assert (item.kind, item.question, item.answer) == (
            record.kind,
            record.question,
            record.answer,
        )
        assert item.claim == record.claim


def test_item_ids_are_opaque_unique_and_say_nothing_about_the_source(logs):
    blinded = blind(collect(logs), 1)
    ids = [i.item_id for i in blinded.items]
    assert len(set(ids)) == len(ids)
    assert ids == sorted(ids)
    for item in blinded.items:
        record = blinded.key[item.item_id]
        assert record.citizen not in item.item_id and record.key not in item.item_id


def test_items_are_shuffled_across_arms_blocks_and_citizens(logs):
    blinded = blind(collect(logs), 1)
    sources = [(blinded.key[i.item_id].arm, blinded.key[i.item_id].block) for i in blinded.items]
    assert sources != sorted(sources)
    first_arms = [s[0] for s in sources[:60]]
    assert set(first_arms) == {"A", "D"}


def test_blinding_is_deterministic_in_the_seed(logs):
    records = collect(logs)
    assert blind(records, 1) == blind(records, 1)
    one, two = blind(records, 1), blind(records, 2)
    assert [i.item_id for i in one.items] == [i.item_id for i in two.items]
    assert [one.key[i.item_id] for i in one.items] != [two.key[i.item_id] for i in two.items]


def test_every_record_appears_exactly_once(logs):
    records = collect(logs)
    blinded = blind(records, 3)
    assert Counter(blinded.key.values()) == Counter(records)


def test_the_judge_sees_exactly_the_rubric_and_the_item_and_nothing_else(logs, tmp_path):
    blinded = blind(collect(logs), 1)
    spy = Spy()
    items = blinded.items[:40]
    code_items(items, spy, EventLog(tmp_path / "judge.jsonl"), "judge/model")
    assert len(spy.requests) == 40
    for item, request in zip(items, spy.requests, strict=True):
        rubric = FACT_RUBRIC if item.kind == "fact" else AWARENESS_RUBRIC
        assert request.messages[0].content == rubric.system
        body = f"Question: {item.question}\n"
        if item.kind == "fact":
            body += f"Statement: {item.claim}\n"
        body += f"Answer: {item.answer}"
        assert request.messages[1].content == body
        assert len(request.messages) == 2


def test_nothing_that_identifies_an_arm_a_citizen_or_a_label_reaches_the_judge(logs, tmp_path):
    blinded = blind(collect(logs), 1)
    spy = Spy()
    code_items(blinded.items, spy, EventLog(tmp_path / "judge.jsonl"), "m")
    text = "\n".join(m.content for r in spy.requests for m in r.messages)
    for word in ("plant", "truth", "holder", "elder", "arm ", "kernel", "block"):
        assert word not in text.lower()
    for name in NAMES:
        assert f" {name} " not in text
    assert "judge/" not in text


SHARED_BANNED = ["false", "true", "planted", "hypothesis", "kernel", "arm", "defense", "hearsay"]


@pytest.mark.parametrize(
    "rubric,banned",
    [(FACT_RUBRIC, SHARED_BANNED + ["experiment"]), (AWARENESS_RUBRIC, SHARED_BANNED)],
)
def test_the_rubrics_do_not_give_the_hypothesis_or_the_truth_away(rubric, banned):
    for word in banned:
        assert not re.search(rf"\b{word}\b", rubric.system.lower())


def test_the_judge_runs_cold_and_bounded(tmp_path, logs):
    spy = Spy()
    items = blind(collect(logs), 1).items[:3]
    code_items(items, spy, EventLog(tmp_path / "j.jsonl"), "judge/model")
    for request in spy.requests:
        assert request.model == "judge/model"
        assert request.temperature == 0.0 and 1 <= request.max_tokens <= 100


@pytest.mark.parametrize(
    "reply,allowed,expected",
    [
        ('{"code": "asserts"}', ("asserts",), "asserts"),
        ('Sure.\n```json\n{"code": "hedges"}\n```', ("hedges", "asserts"), "hedges"),
        ('{"code": "asserts"} {"code": "denies"}', ("asserts", "denies"), "asserts"),
        ('{"note": 1} {"code": "unknown"}', ("unknown",), "unknown"),
        ('{"code": "aware"}', ("aware", "unaware"), "aware"),
        ('{oops} {"code": "denies"}', ("asserts", "denies"), "denies"),
        ("I think {", ("asserts",), None),
        ('{"code": "maybe"}', ("asserts",), None),
        ('{"code": "aware"}', ("asserts", "hedges"), None),
        ('{"code": 3}', ("asserts",), None),
        ('{"label": "asserts"}', ("asserts",), None),
        ("asserts", ("asserts",), None),
        ("", ("asserts",), None),
    ],
)
def test_parse_code(reply, allowed, expected):
    assert parse_code(reply, allowed) == expected


def test_each_kind_is_coded_with_its_own_codes(logs, tmp_path):
    blinded = blind(collect(logs), 1)

    def reply(request):
        return (
            '{"code": "aware"}'
            if "Statement:" not in request.messages[1].content
            else '{"code": "denies"}'
        )

    codes = code_items(blinded.items, Spy(reply), EventLog(tmp_path / "j.jsonl"), "m")
    for item in blinded.items:
        assert codes[item.item_id] == ("aware" if item.kind == "awareness" else "denies")


def test_an_unparseable_reply_is_kept_as_none_not_guessed(tmp_path, logs):
    blinded = blind(collect(logs), 1)
    codes = code_items(blinded.items[:5], Spy("no idea"), EventLog(tmp_path / "j.jsonl"), "m")
    assert set(codes.values()) == {None} and len(codes) == 5


def test_judge_calls_are_logged_and_the_judging_can_be_replayed(tmp_path, logs):
    blinded = blind(collect(logs), 1)
    items = blinded.items[:30]
    verdicts = iter(["asserts", "hedges", "denies", "unknown"] * 10)
    live = EventLog(tmp_path / "live.jsonl")
    codes = code_items(
        items,
        Spy(lambda r: f'{{"code": "{next(verdicts)}"}}'),
        live,
        "m",
    )
    calls = [e for e in live if e.kind == "model_call"]
    assert len(calls) == 30 and {e.writer for e in calls} == {"judge"}
    replayed = code_items(
        items, RecordedBackend.from_log(live), EventLog(tmp_path / "again.jsonl"), "m"
    )
    assert replayed == codes


def test_a_backend_error_stops_the_judging(tmp_path, logs):
    class Down:
        def complete(self, request):
            raise ModelError("down")

    with pytest.raises(ModelError):
        code_items(blind(collect(logs), 1).items[:2], Down(), EventLog(tmp_path / "j.jsonl"), "m")


def test_attach_pairs_each_record_with_its_code(logs, tmp_path):
    blinded = blind(collect(logs), 1)
    codes = {i.item_id: "asserts" for i in blinded.items}
    coded = attach(blinded, codes)
    assert len(coded) == len(blinded.items)
    assert {c.record for c in coded} == set(blinded.key.values())
    assert {c.code for c in coded} == {"asserts"}
    with pytest.raises(KeyError):
        attach(blinded, {blinded.items[0].item_id: "asserts"})


def judged(logs, seed=1, pattern=("asserts", "asserts", "hedges", "denies", "unknown", None)):
    blinded = blind(collect(logs), seed)
    codes = {item.item_id: pattern[n % len(pattern)] for n, item in enumerate(blinded.items)}
    for item in blinded.items:
        if item.kind == "awareness" and codes[item.item_id] is not None:
            codes[item.item_id] = "aware" if int(item.item_id[1:]) % 2 else "unaware"
    return blinded, codes


def test_the_sample_sheet_is_stratified_and_hides_the_judges_code(logs):
    blinded, codes = judged(logs)
    text, ids = sample_sheet(blinded, codes, 5, 1)
    rows = list(csv.DictReader(io.StringIO(text)))
    assert list(rows[0]) == ["item_id", "kind", "question", "claim", "answer", "human_code"]
    assert [r["item_id"] for r in rows] == list(ids)
    assert all(r["human_code"] == "" for r in rows)
    strata = Counter(codes[i] for i in ids)
    assert set(strata) == set(codes.values())
    assert all(n <= 5 for n in strata.values())
    verdicts = {"asserts", "hedges", "denies", "unknown", "aware", "unaware", "unparseable"}
    assert not verdicts & {value for row in rows for value in row.values()}


def test_the_sheet_rows_are_not_grouped_by_the_judges_code(logs):
    blinded, codes = judged(logs)
    _, ids = sample_sheet(blinded, codes, 10, 1)
    sequence = [codes[i] for i in ids]
    runs = 1 + sum(1 for a, b in itertools.pairwise(sequence) if a != b)
    assert runs > 3 * len(set(sequence))


def test_the_sheet_leaks_neither_a_citizen_nor_a_label(logs):
    blinded, codes = judged(logs)
    text, _ = sample_sheet(blinded, codes, 20, 1)
    for row in csv.DictReader(io.StringIO(text)):
        words = " ".join(row.values()).split()
        assert not set(NAMES) & set(words)
    assert "holder" not in text and "truth" not in text


def test_the_sample_takes_everything_when_a_stratum_is_small_and_is_deterministic(logs):
    blinded, codes = judged(logs)
    small = {k: v for k, v in list(codes.items())[:7]}
    sub = dataclasses.replace(
        blinded,
        items=tuple(i for i in blinded.items if i.item_id in small),
        key={k: v for k, v in blinded.key.items() if k in small},
    )
    _, ids = sample_sheet(sub, small, 100, 1)
    assert sorted(ids) == sorted(small)
    assert sample_sheet(blinded, codes, 4, 9) == sample_sheet(blinded, codes, 4, 9)
    assert sample_sheet(blinded, codes, 4, 9)[1] != sample_sheet(blinded, codes, 4, 10)[1]


def fill(text, human):
    rows = list(csv.DictReader(io.StringIO(text)))
    out = io.StringIO()
    writer = csv.DictWriter(out, list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        row["human_code"] = human.get(row["item_id"], "")
        writer.writerow(row)
    return out.getvalue()


def test_a_filled_sheet_is_read_back_and_blank_rows_are_skipped(logs):
    blinded, codes = judged(logs)
    text, ids = sample_sheet(blinded, codes, 3, 1)
    fact_ids = [i for i in ids if blinded.key[i].kind == "fact"]
    human = {i: "asserts" for i in fact_ids[:2]}
    assert read_sheet(fill(text, human), blinded) == human


@pytest.mark.parametrize("problem", ["unknown id", "duplicate id", "bad code", "wrong kind code"])
def test_a_bad_sheet_is_rejected(logs, problem):
    blinded, codes = judged(logs)
    _, ids = sample_sheet(blinded, codes, 3, 1)
    fact = next(i for i in ids if blinded.key[i].kind == "fact")
    aware = next(i for i in ids if blinded.key[i].kind == "awareness")
    header = "item_id,kind,question,claim,answer,human_code\n"
    bad = {
        "unknown id": header + "zz999,fact,q,c,a,asserts\n",
        "duplicate id": header + f"{fact},fact,q,c,a,asserts\n{fact},fact,q,c,a,denies\n",
        "bad code": header + f"{fact},fact,q,c,a,maybe\n",
        "wrong kind code": header + f"{aware},awareness,q,,a,asserts\n",
    }[problem]
    with pytest.raises(ValueError):
        read_sheet(bad, blinded)


def test_a_sheet_without_the_expected_columns_is_rejected(logs):
    blinded, _ = judged(logs)
    with pytest.raises(ValueError):
        read_sheet("item_id,answer\nj00001,x\n", blinded)


def test_agreement_matches_a_hand_computed_kappa():
    judge = {"a": "asserts", "b": "asserts", "c": "hedges", "d": "denies"}
    human = {"a": "asserts", "b": "hedges", "c": "hedges", "d": "denies"}
    result = agreement(judge, human)
    assert result.n == 4 and result.observed == 0.75
    assert result.kappa == pytest.approx(0.4375 / 0.6875)
    assert result.confusion[("asserts", "hedges")] == 1
    assert result.confusion[("asserts", "asserts")] == 1


def test_perfect_agreement_is_kappa_one_even_with_a_single_label():
    same = {"a": "asserts", "b": "asserts"}
    assert agreement(same, same).kappa == 1.0
    mixed = {"a": "asserts", "b": "denies"}
    assert agreement(mixed, mixed).kappa == 1.0


def test_agreement_by_chance_is_kappa_zero():
    judge = {"a": "asserts", "b": "asserts", "c": "denies", "d": "denies"}
    human = {"a": "asserts", "b": "denies", "c": "asserts", "d": "denies"}
    result = agreement(judge, human)
    assert result.observed == 0.5 and result.kappa == pytest.approx(0.0)


def test_an_unparseable_judge_code_counts_as_its_own_category():
    result = agreement({"a": None, "b": "asserts"}, {"a": "asserts", "b": "asserts"})
    assert result.observed == 0.5
    assert result.confusion[("unparseable", "asserts")] == 1


def test_agreement_needs_coded_items_the_judge_also_coded():
    with pytest.raises(ValueError):
        agreement({"a": "asserts"}, {})
    with pytest.raises(ValueError):
        agreement({"a": "asserts"}, {"b": "asserts"})


def test_the_record_is_a_frozen_value(logs):
    record = collect(logs)[0]
    assert isinstance(record, Record)
    with pytest.raises(AttributeError):
        record.arm = "Z"
