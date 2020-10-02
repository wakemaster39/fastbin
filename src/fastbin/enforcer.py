from casbin import Enforcer as CasbinEnforcer
from casbin.model import Model as CasbinModel

from fastbin.policy import FilteredPolicy


class Model(CasbinModel):
    def add_def(self, sec, key, value):
        super().add_def(sec, key, value)
        if sec == "p" and key == "p":
            self.model[sec][key].policy = FilteredPolicy()


class FastEnforcer(CasbinEnforcer):
    @staticmethod
    def new_model(path: str = "", text: str = "") -> Model:
        """creates a model."""

        m = Model()
        if len(path) > 0:
            m.load_model(path)
        else:
            m.load_model_from_text(text)

        return m

    def enforce(self, *rvals: str) -> bool:
        self.model.model["p"]["p"].policy.apply_filter(rvals[1], rvals[2])
        result = super().enforce(*rvals)
        self.model.model["p"]["p"].policy.clear_filter()
        return result
