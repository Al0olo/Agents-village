import itertools
import random

import pytest

from agent_village.admission import Admission, Claim, Event, Kind, admit, admit_corroborated


def log(*events):
    return {e.id: e for e in events}


def test_first_hand_event_admits():
    l = log(Event("e1", "ada", Kind.SEEN))
    assert admit(Claim("the well is dry", "ada", ("e1",)), l) is Admission.FACT


def test_no_citation_is_hearsay():
    assert admit(Claim("the well is dry", "ada", ()), {}) is Admission.HEARSAY


def test_two_told_events_from_one_origin_are_hearsay():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_two_told_events_with_disjoint_origins_admit():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"cy"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.FACT


def test_forwarded_chain_does_not_launder_an_origin():
    # Cy forwarded Bo's message, so both told-events trace back to Bo.
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_cannot_cite_another_citizens_log():
    l = log(Event("e1", "bo", Kind.SEEN))
    assert admit(Claim("x", "ada", ("e1",)), l) is Admission.HEARSAY


def test_citing_the_same_told_event_twice_is_one_source():
    l = log(Event("e1", "ada", Kind.TOLD, frozenset({"bo"})))
    assert admit(Claim("x", "ada", ("e1", "e1")), l) is Admission.HEARSAY


def test_every_event_in_a_forward_chain_shares_the_root():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
        Event("e3", "ada", Kind.TOLD, frozenset({"bo", "cy", "di"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2", "e3")), l) is Admission.HEARSAY


def test_a_forward_chain_does_not_hide_an_independent_source():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
        Event("e3", "ada", Kind.TOLD, frozenset({"di"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2", "e3")), l) is Admission.FACT


def test_two_chains_with_no_shared_origin_are_independent():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"di", "ed"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.FACT


def test_partially_overlapping_chains_are_not_independent():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"cy", "di"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_told_events_without_origins_never_count():
    none = log(
        Event("e1", "ada", Kind.TOLD),
        Event("e2", "ada", Kind.TOLD),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), none) is Admission.HEARSAY
    one = log(
        Event("e1", "ada", Kind.TOLD),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), one) is Admission.HEARSAY


def test_another_citizens_told_event_does_not_make_a_second_source():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "cy", Kind.TOLD, frozenset({"di"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_unknown_citations_are_ignored_next_to_real_evidence():
    l = log(Event("e1", "ada", Kind.DID))
    assert admit(Claim("x", "ada", ("nope", "e1", "")), l) is Admission.FACT


def test_colluding_senders_are_independent_origins_by_design():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"mal1"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"mal2"})),
    )
    assert admit(Claim("lie", "ada", ("e1", "e2")), l) is Admission.FACT


def test_a_colluder_forwarding_the_other_is_caught():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"mal1"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"mal1", "mal2"})),
    )
    assert admit(Claim("lie", "ada", ("e1", "e2")), l) is Admission.HEARSAY


@pytest.mark.parametrize(
    "events,cites,expected",
    [
        (
            [
                Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
                Event("e2", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
                Event("e3", "ada", Kind.TOLD, frozenset({"di"})),
                Event("e4", "cy", Kind.SEEN),
            ],
            ("e1", "e2", "e3", "e4", "e5"),
            Admission.FACT,
        ),
        (
            [
                Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
                Event("e2", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
                Event("e4", "cy", Kind.SEEN),
            ],
            ("e1", "e2", "e4", "e5"),
            Admission.HEARSAY,
        ),
    ],
)
def test_the_decision_does_not_depend_on_citation_order(events, cites, expected):
    l = log(*events)
    results = {admit(Claim("x", "ada", order), l) for order in itertools.permutations(cites)}
    assert results == {expected}


def test_admission_is_pure():
    l = log(Event("e1", "ada", Kind.SEEN))
    before = dict(l)
    claim = Claim("x", "ada", ("e1",))
    assert admit(claim, l) is admit(claim, l)
    assert l == before


def test_a_told_event_that_originates_with_the_writer_is_not_evidence():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"ada", "bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"cy"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_two_echoes_of_the_writers_own_claim_are_not_two_sources():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"ada", "bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"ada", "cy"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_an_echo_does_not_block_a_genuine_pair():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"ada", "bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"cy"})),
        Event("e3", "ada", Kind.TOLD, frozenset({"di"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2", "e3")), l) is Admission.FACT


def test_the_writer_as_the_only_origin_is_an_echo_too():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"ada"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo"})),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.HEARSAY


def test_an_echo_does_not_cancel_first_hand_evidence():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"ada", "bo"})),
        Event("e2", "ada", Kind.SEEN),
    )
    assert admit(Claim("x", "ada", ("e1", "e2")), l) is Admission.FACT


def shared(text, writer, *cites):
    return Claim(text, writer, cites, shared=True)


def test_a_claim_does_not_ask_for_the_shared_tier_unless_it_says_so():
    assert Claim("x", "ada", ()).shared is False


def test_the_corroborated_policy_is_the_kernels_for_a_private_claim():
    l = log(Event("e1", "ada", Kind.SEEN), Event("e2", "ada", Kind.TOLD, frozenset({"bo"})))
    for cites in [(), ("e1",), ("e2",), ("e1", "e2"), ("e9",)]:
        claim = Claim("x", "ada", cites)
        assert admit_corroborated(claim, l) is admit(claim, l)


def test_a_lone_first_hand_witness_cannot_publish_to_the_shared_tier():
    l = log(Event("e1", "ada", Kind.SEEN))
    assert admit(shared("x", "ada", "e1"), l) is Admission.FACT
    assert admit_corroborated(shared("x", "ada", "e1"), l) is Admission.HEARSAY


def test_repeating_ones_own_observation_is_still_one_source():
    l = log(Event("e1", "ada", Kind.SEEN), Event("e2", "ada", Kind.DID))
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.HEARSAY
    assert admit_corroborated(shared("x", "ada", "e1", "e1"), l) is Admission.HEARSAY


def test_a_first_hand_witness_with_an_independent_told_source_can_publish():
    l = log(Event("e1", "ada", Kind.SEEN), Event("e2", "ada", Kind.TOLD, frozenset({"bo"})))
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.FACT


def test_an_action_the_writer_took_corroborates_like_an_observation():
    l = log(Event("e1", "ada", Kind.DID), Event("e2", "ada", Kind.TOLD, frozenset({"bo"})))
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.FACT


def test_a_told_event_with_no_recorded_origin_is_not_a_source():
    l = log(
        Event("e1", "ada", Kind.SEEN),
        Event("e2", "ada", Kind.TOLD),
        Event("e3", "ada", Kind.TOLD),
    )
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.HEARSAY
    assert admit_corroborated(shared("x", "ada", "e2", "e3"), l) is Admission.HEARSAY


def test_a_told_source_that_traces_back_to_the_writer_does_not_corroborate():
    l = log(
        Event("e1", "ada", Kind.SEEN),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo", "ada"})),
    )
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.HEARSAY


def test_two_independent_told_sources_publish_as_under_the_kernel():
    l = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"cy"})),
    )
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.FACT
    same = log(
        Event("e1", "ada", Kind.TOLD, frozenset({"bo"})),
        Event("e2", "ada", Kind.TOLD, frozenset({"bo", "cy"})),
    )
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), same) is Admission.HEARSAY


def test_another_citizens_events_do_not_count_toward_corroboration():
    l = log(Event("e1", "bo", Kind.SEEN), Event("e2", "ada", Kind.SEEN))
    assert admit_corroborated(shared("x", "ada", "e1", "e2"), l) is Admission.HEARSAY


@pytest.mark.parametrize("seed", range(5))
def test_the_corroborated_policy_never_admits_what_the_kernel_would_refuse(seed):
    names = ["ada", "bo", "cy"]
    kinds = [Kind.SEEN, Kind.DID, Kind.TOLD]
    pool = [
        Event(f"e{i}", n, k, frozenset(o) if k is Kind.TOLD else frozenset())
        for i, (n, k, o) in enumerate(
            itertools.product(names, kinds, [{"bo"}, {"cy"}, {"bo", "cy"}, {"ada"}, {"ada", "bo"}])
        )
    ]
    l = log(*pool)
    rng = random.Random(seed)
    for _ in range(300):
        cites = tuple(e.id for e in rng.sample(pool, rng.randint(0, 4)))
        claim = shared("x", rng.choice(names), *cites)
        if admit_corroborated(claim, l) is Admission.FACT:
            assert admit(claim, l) is Admission.FACT
