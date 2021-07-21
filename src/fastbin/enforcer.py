from typing import Any, Sequence, TypeVar, cast

from casbin import Enforcer as CasbinEnforcer
from casbin.model import Model as CasbinModel
from casbin.model import Policy

from fastbin.policy import FilterablePolicy, filter_policy


class Model(CasbinModel):
    _cache_key_order: Sequence[int]

    def __init__(self, cache_key_order: Sequence[int]) -> None:
        super().__init__()
        self._cache_key_order = cache_key_order

    def add_def(self, sec: str, key: str, value: Any) -> None:
        super().add_def(sec, key, value)
        if sec == "p" and key == "p":
            self.model[sec][key].policy = FilterablePolicy(self._cache_key_order)

    def clear_policy(self) -> None:
        """clears all current policy."""
        super().clear_policy()
        self.model["p"]["p"].policy = FilterablePolicy(self._cache_key_order)


T = TypeVar("T", bound=CasbinModel)
T2 = TypeVar("T2", bound=Policy)


class FastEnforcer(CasbinEnforcer):
    _cache_key_order: Sequence[int]

    def __init__(
        self,
        cache_key_order: Sequence[int],
        model: T = None,
        adapter: T2 = None,
    ):
        self._cache_key_order = cache_key_order
        super().__init__(model=model, adapter=adapter)

    def new_model(self, path: str = "", text: str = "") -> Model:
        """creates a model."""

        m = Model(self._cache_key_order)
        if len(path) > 0:
            m.load_model(path)
        else:
            m.load_model_from_text(text)

        return m

    def enforce(self, *rvals: str) -> bool:
        keys = [rvals[x] for x in self._cache_key_order]
        with filter_policy(self.model.model["p"]["p"].policy, *keys):
            return cast(bool, super().enforce(*rvals))
