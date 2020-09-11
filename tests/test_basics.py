import os
import matplotlib

matplotlib.use("Agg")
from topkappy import (
    KappaModel,
    KappaAgent,
    KappaRule,
    KappaSiteState,
    plot_simulation_time_series,
    plot_snapshot_agents,
    FormattedKappaError,
)


def test_basic_example(tmpdir):
    model = KappaModel(
        agents=[
            KappaAgent("A", ("a", "b")),
            KappaAgent("B", ("b", "c")),
            KappaAgent("C", ("c", "d")),
        ],
        rules=[
            KappaRule(
                "a.b",
                [KappaSiteState("A", "b", "."), KappaSiteState("B", "b", ".")],
                "->",
                [KappaSiteState("A", "b", "1"), KappaSiteState("B", "b", "1")],
                rate=0.5e-2,
            ),
            KappaRule(
                "b.c",
                [KappaSiteState("B", "c", "."), KappaSiteState("C", "c", ".")],
                "->",
                [KappaSiteState("B", "c", "1"), KappaSiteState("C", "c", "1")],
                rate=2.1e-2,
            ),
        ],
        initial_quantities={"A": 100, "B": 100, "C": 100,},
        duration=10,
        snapshot_times={"end": 10},
        plots=[KappaSiteState("B", "b", "."), KappaSiteState("C", "c", ".")],
    )

    simulation_results = model.get_simulation_results()

    ax = plot_simulation_time_series(simulation_results["plots"])
    ax.figure.savefig(os.path.join(str(tmpdir), "time_series.png"))

    agents_at_end = simulation_results["snapshots"]["end"]["snapshot_agents"]
    fig, axes = plot_snapshot_agents(agents_at_end)
    fig.savefig(os.path.join(str(tmpdir), "snapshot.png"))


def test_error():
    model = KappaModel(
        agents=[
            KappaAgent("A", ("a", "b")),
            KappaAgent("B", ("b", "c")),
            KappaAgent("C", ("c", "d")),
            KappaAgent("D", ("c", "d")),
            KappaAgent("E;## THIS ERROR", ("c", "d")),
        ],
        rules=[],
        initial_quantities={},
        duration=10,
        snapshot_times={},
        plots=[],
    )
    errored = False
    try:
        simulation_results = model.get_simulation_results()
    except FormattedKappaError as err:
        assert "THIS" in str(err)
        errored = True
    assert errored
