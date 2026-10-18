from agent_village.admission import Admission, Claim, Event, Kind, admit


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
