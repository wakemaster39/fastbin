from pathlib import Path

from fastbin.enforcer import FastEnforcer
from fastbin.policy import FilterablePolicy


def get_test_file(file_name: str) -> str:
    tests_folder = Path(__file__).parent.parent / "models"
    return str(tests_folder / file_name)


class TestFastEnforcer:
    def test_creates_proper_policy(self) -> None:
        enforcer = FastEnforcer(
            [2, 1],
            get_test_file("basic_model.conf"),
            get_test_file("basic_policy.csv"),
        )

        assert isinstance(enforcer.model.model["p"]["p"].policy, FilterablePolicy)

    def test_initializes_model(self) -> None:
        enforcer = FastEnforcer(
            [2, 1],
            get_test_file("basic_model.conf"),
            get_test_file("basic_policy.csv"),
        )

        assert list(enforcer.model.model["p"]["p"].policy) == [
            ["alice", "data1", "read"],
            ["bob", "data2", "write"],
        ]

    def test_able_to_clear_policy(self) -> None:
        enforcer = FastEnforcer(
            [2, 1],
            get_test_file("basic_model.conf"),
            get_test_file("basic_policy.csv"),
        )

        enforcer.clear_policy()

        assert isinstance(enforcer.model.model["p"]["p"].policy, FilterablePolicy)
        assert list(enforcer.model.model["p"]["p"].policy) == []

    def test_able_to_enforce_rule(self) -> None:
        enforcer = FastEnforcer(
            [2, 1],
            get_test_file("basic_model.conf"),
            get_test_file("basic_policy.csv"),
        )

        assert enforcer.enforce("alice", "data1", "read")
        assert not enforcer.enforce("alice2", "data1", "read")
