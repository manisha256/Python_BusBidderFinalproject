from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ProfileSpec:
    key: str
    label: str
    name: str
    email: str
    phone: str
    traveller_type: str
    max_budget: float
    max_transfers: int
    max_duration: int
    require_changeable: bool
    preferred_time: str
    weights: Dict[str, float]


class TravellerProfileRegistry:
    """Registry using a class-level dict and decorator for dynamic profile discovery."""

    _registry: Dict[str, ProfileSpec] = {}

    @classmethod
    def register(cls, key: str) -> Callable[[Callable[[], ProfileSpec]], Callable[[], ProfileSpec]]:
        """Decorator that registers the ProfileSpec returned by a profile factory function."""
        def decorator(factory_fn: Callable[[], ProfileSpec]) -> Callable[[], ProfileSpec]:
            spec = factory_fn()
            cls._registry[str(key)] = spec
            return factory_fn
        return decorator

    @classmethod
    def get(cls, key: str) -> Optional[ProfileSpec]:
        return cls._registry.get(str(key))

    @classmethod
    def all_profiles(cls) -> List[Tuple[str, ProfileSpec]]:
        """Dynamically discovers all registered profiles sorted by numeric key."""
        return sorted(
            cls._registry.items(),
            key=lambda pair: int(pair[0]) if pair[0].isdigit() else 999,
        )


@TravellerProfileRegistry.register("1")
def _business_profile() -> ProfileSpec:
    return ProfileSpec(
        key="1",
        label="Business Traveller",
        name="Ana Business",
        email="ana@business.es",
        phone="611223344",
        traveller_type="business",
        max_budget=150.0,
        max_transfers=1,
        max_duration=480,
        require_changeable=True,
        preferred_time="Morning",
        weights={"price": 0.20, "duration": 0.40, "time": 0.20, "flexibility": 0.20},
    )


@TravellerProfileRegistry.register("2")
def _budget_profile() -> ProfileSpec:
    return ProfileSpec(
        key="2",
        label="Budget Traveller",
        name="Carlos Student",
        email="carlos@economy.es",
        phone="622334455",
        traveller_type="economical",
        max_budget=60.0,
        max_transfers=2,
        max_duration=600,
        require_changeable=False,
        preferred_time="Morning",
        weights={"price": 0.60, "duration": 0.20, "time": 0.10, "flexibility": 0.10},
    )


@TravellerProfileRegistry.register("3")
def _eco_profile() -> ProfileSpec:
    return ProfileSpec(
        key="3",
        label="Environment-Focused Traveller",
        name="Elena Green",
        email="elena@eco.es",
        phone="633445566",
        traveller_type="environment_friendly",
        max_budget=120.0,
        max_transfers=0,
        max_duration=540,
        require_changeable=False,
        preferred_time="Morning",
        weights={"price": 0.25, "duration": 0.35, "time": 0.15, "flexibility": 0.25},
    )


@TravellerProfileRegistry.register("4")
def _flexible_profile() -> ProfileSpec:
    return ProfileSpec(
        key="4",
        label="Flexibility-Focused Tourist",
        name="Fiona Flexible",
        email="fiona@flex.es",
        phone="644556677",
        traveller_type="flexible",
        max_budget=130.0,
        max_transfers=1,
        max_duration=540,
        require_changeable=True,
        preferred_time="Afternoon",
        weights={"price": 0.20, "duration": 0.20, "time": 0.15, "flexibility": 0.45},
    )