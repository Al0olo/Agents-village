import pytest

from agent_village.admission import Admission, Kind, admit, admit_corroborated
from agent_village.eventlog import EventLog
from agent_village.memory import Memory, Tier


def setup(tmp_path, policy=admit):
    log = EventLog(tmp_path / "v.jsonl")
    return log, Memory(log, policy)


def told(log, who, origins):
    return str(log.append("told", who, {"origins": sorted(origins)}).id)


def test_claim_citing_own_observation_is_fact_in_core(tmp_path):
    log, memory = setup(tmp_path)
    seen = str(log.append("saw", "ada", {"what": "well"}).id)
    entry = memory.write_claim("ada", "the well is dry", Kind.SEEN, (seen,), Tier.CORE)
    assert entry.admission is Admission.FACT
    assert entry.tier is Tier.CORE
    assert memory.entries(Tier.CORE, "ada") == (entry,)
    assert memory.entries(Tier.RECALL, "ada") == ()


def test_fact_written_to_shared_is_visible_to_everyone(tmp_path):
    log, memory = setup(tmp_path)
    did = str(log.append("did", "ada", {"act": "dig"}).id)
    entry = memory.write_claim("ada", "the well is dry", Kind.DID, (did,), Tier.SHARED)
    assert memory.entries(Tier.SHARED) == (entry,)
    assert memory.entries(Tier.SHARED, "bo") == (entry,)


def test_uncited_claim_is_stored_as_hearsay_in_recall(tmp_path):
    _, memory = setup(tmp_path)
    entry = memory.write_claim("ada", "the well is dry", Kind.TOLD, (), Tier.SHARED)
    assert entry.admission is Admission.HEARSAY
    assert entry.tier is Tier.RECALL
    assert entry.requested is Tier.SHARED
    assert memory.entries(Tier.SHARED) == ()
    assert memory.entries(Tier.RECALL, "ada") == (entry,)


def test_declared_kind_is_recorded_but_never_trusted(tmp_path):
    _, memory = setup(tmp_path)
    entry = memory.write_claim("ada", "the well is dry", Kind.SEEN, (), Tier.CORE)
    assert entry.kind is Kind.SEEN
    assert entry.admission is Admission.HEARSAY


def test_citing_another_citizens_observation_is_hearsay(tmp_path):
    log, memory = setup(tmp_path)
    seen = str(log.append("saw", "ada", {}).id)
    entry = memory.write_claim("bo", "the well is dry", Kind.SEEN, (seen,), Tier.SHARED)
    assert entry.admission is Admission.HEARSAY


def test_two_told_events_with_disjoint_origins_are_fact(tmp_path):
    log, memory = setup(tmp_path)
    cites = (told(log, "ada", {"bo"}), told(log, "ada", {"cy"}))
    entry = memory.write_claim("ada", "x", Kind.TOLD, cites, Tier.CORE)
    assert entry.admission is Admission.FACT


def test_forwarded_origin_cannot_be_laundered_into_fact(tmp_path):
    log, memory = setup(tmp_path)
    cites = (told(log, "ada", {"bo"}), told(log, "ada", {"bo", "cy"}))
    entry = memory.write_claim("ada", "x", Kind.TOLD, cites, Tier.CORE)
    assert entry.admission is Admission.HEARSAY


def test_only_perceptions_and_actions_count_as_evidence(tmp_path):
    log, memory = setup(tmp_path)
    call = str(log.append("model_call", "ada", {"text": "the well is dry"}).id)
    earlier = memory.write_claim("ada", "the well is dry", Kind.SEEN, (call,), Tier.CORE)
    laundered = memory.write_claim("ada", "again", Kind.SEEN, (str(earlier.id),), Tier.CORE)
    assert earlier.admission is Admission.HEARSAY
    assert laundered.admission is Admission.HEARSAY


@pytest.mark.parametrize("cite", ["99", "-1", "abc", ""])
def test_unresolvable_citations_are_hearsay(tmp_path, cite):
    _, memory = setup(tmp_path)
    entry = memory.write_claim("ada", "x", Kind.SEEN, (cite,), Tier.CORE)
    assert entry.admission is Admission.HEARSAY


def test_core_and_recall_are_private_to_their_writer(tmp_path):
    log, memory = setup(tmp_path)
    seen = str(log.append("saw", "ada", {}).id)
    memory.write_claim("ada", "a", Kind.SEEN, (seen,), Tier.CORE)
    memory.write_claim("ada", "b", Kind.SEEN, (), Tier.CORE)
    assert memory.entries(Tier.CORE, "bo") == ()
    assert memory.entries(Tier.RECALL, "bo") == ()
    assert [e.text for e in memory.entries(Tier.CORE, "ada")] == ["a"]
    assert [e.text for e in memory.entries(Tier.RECALL, "ada")] == ["b"]


def test_entries_follow_log_order(tmp_path):
    log, memory = setup(tmp_path)
    seen = str(log.append("saw", "ada", {}).id)
    for text in ("one", "two", "three"):
        memory.write_claim("ada", text, Kind.SEEN, (seen,), Tier.SHARED)
    entries = memory.entries(Tier.SHARED)
    assert [e.text for e in entries] == ["one", "two", "three"]
    assert [e.id for e in entries] == sorted(e.id for e in entries)


def test_policy_is_injected(tmp_path):
    _, memory = setup(tmp_path, policy=lambda claim, events: Admission.FACT)
    entry = memory.write_claim("ada", "x", Kind.TOLD, (), Tier.SHARED)
    assert entry.tier is Tier.SHARED


def test_rebuild_from_the_log_equals_live_without_rerunning_the_policy(tmp_path):
    log, memory = setup(tmp_path)
    seen = str(log.append("saw", "ada", {}).id)
    memory.write_claim("ada", "a", Kind.SEEN, (seen,), Tier.CORE)
    memory.write_claim("ada", "b", Kind.TOLD, (), Tier.SHARED)
    memory.write_claim("bo", "c", Kind.SEEN, (seen,), Tier.SHARED)

    calls = []
    rebuilt = Memory(EventLog(tmp_path / "v.jsonl"), lambda c, e: calls.append(c))
    for tier in Tier:
        for who in ("ada", "bo"):
            assert rebuilt.entries(tier, who) == memory.entries(tier, who)
    assert calls == []


def test_events_logged_after_construction_can_be_cited(tmp_path):
    log, memory = setup(tmp_path)
    seen = str(log.append("saw", "ada", {}).id)
    entry = memory.write_claim("ada", "x", Kind.SEEN, (seen,), Tier.CORE)
    assert entry.admission is Admission.FACT


def test_the_decision_is_in_the_log(tmp_path):
    log, memory = setup(tmp_path)
    memory.write_claim("ada", "x", Kind.SEEN, (), Tier.CORE)
    event = list(log)[-1]
    assert event.kind == "claim"
    assert event.writer == "ada"
    assert event.payload == {
        "text": "x",
        "kind": "seen",
        "cites": [],
        "requested": "core",
        "admission": "hearsay",
        "stored": "recall",
    }


@pytest.mark.parametrize(
    "writer,text,tier",
    [("", "x", Tier.CORE), ("ada", "", Tier.CORE), ("ada", "x", Tier.RECALL)],
)
def test_invalid_writes_are_rejected_without_logging(tmp_path, writer, text, tier):
    log, memory = setup(tmp_path)
    with pytest.raises(ValueError):
        memory.write_claim(writer, text, Kind.SEEN, (), tier)
    assert len(log) == 0


@pytest.mark.parametrize("tier,asks", [(Tier.CORE, False), (Tier.SHARED, True)])
def test_the_policy_is_told_whether_the_claim_asks_for_the_shared_tier(tmp_path, tier, asks):
    seen = []

    def spy(claim, evidence):
        seen.append(claim)
        return Admission.FACT

    _, memory = setup(tmp_path, spy)
    memory.write_claim("ada", "x", Kind.SEEN, (), tier)
    assert [c.shared for c in seen] == [asks]


def test_a_lone_witness_reaches_core_but_not_the_wiki_under_the_corroborated_policy(tmp_path):
    log, memory = setup(tmp_path, admit_corroborated)
    seen = str(log.append("saw", "ada", {"what": "well"}).id)
    core = memory.write_claim("ada", "the well is dry", Kind.SEEN, (seen,), Tier.CORE)
    wiki = memory.write_claim("ada", "the well is dry", Kind.SEEN, (seen,), Tier.SHARED)
    assert (core.admission, core.tier) == (Admission.FACT, Tier.CORE)
    assert (wiki.admission, wiki.tier) == (Admission.HEARSAY, Tier.RECALL)
    assert memory.entries(Tier.SHARED) == ()


def heard(log, who, origin):
    return str(log.append("heard", who, {"from": "a traveler", "origins": [origin]}).id)


def test_a_rumor_a_traveler_told_is_told_evidence_with_its_own_origin(tmp_path):
    log, memory = setup(tmp_path)
    one = heard(log, "ada", "traveler:f1")
    entry = memory.write_claim("ada", "x", Kind.TOLD, (one,), Tier.SHARED)
    assert (entry.admission, entry.tier) == (Admission.HEARSAY, Tier.RECALL)
    two = heard(log, "ada", "traveler:f2")
    both = memory.write_claim("ada", "x", Kind.TOLD, (one, two), Tier.SHARED)
    assert both.admission is Admission.FACT


def test_a_rumor_is_never_first_hand_evidence(tmp_path):
    log, memory = setup(tmp_path)
    one = heard(log, "ada", "traveler:f1")
    entry = memory.write_claim("ada", "x", Kind.SEEN, (one,), Tier.CORE)
    assert entry.admission is Admission.HEARSAY


def test_a_rumor_cannot_back_another_citizens_claim(tmp_path):
    log, memory = setup(tmp_path)
    one = heard(log, "ada", "traveler:f1")
    two = heard(log, "ada", "traveler:f2")
    assert memory.write_claim("bo", "x", Kind.TOLD, (one, two), Tier.SHARED).admission is (
        Admission.HEARSAY
    )
