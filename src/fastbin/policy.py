from typing import Sequence, Set, Optional, Dict, Iterable, Any, Tuple


def in_cache(cache: Dict[str, Any], keys: Sequence[str]) -> Tuple[bool, Optional[Set[Sequence[str]]]]:
    if keys[0] in cache:
        if len(keys) > 1:
            return in_cache(cache[keys[-0]], keys[1:])
        return True, cache[keys[0]]
    else:
        return False, None


class FilteredPolicy:
    _cache: Dict[str, Dict[str, Set[Sequence[str]]]]
    _current_filter: Optional[Set[Sequence[str]]]
    _cache_key_order: Sequence[int]

    def __init__(self, cache_key_order: Sequence[int]) -> None:
        self._cache = {}
        self._current_filter = None
        self._cache_key_order = cache_key_order

    def __iter__(self) -> Iterable[Sequence[str]]:
        yield from self.__get_policy()

    def __len__(self) -> int:
        return len(list(self.__get_policy()))

    def __contains__(self, item: Sequence[str]) -> bool:
        keys = [item[x] for x in self._cache_key_order]
        exists, value = in_cache(self._cache, keys)
        if not exists:
            return False
        return tuple(item) in value

    def append(self, item: Sequence[str]) -> None:
        cache = self._cache
        keys = [item[x] for x in self._cache_key_order]

        for key in keys:
            if key not in cache:
                cache[key] = set()
            cache = cache[key]

        cache.add(tuple(item))

    def remove(self, policy: Sequence[str]) -> bool:
        keys = [policy[x] for x in self._cache_key_order]
        exists, value = in_cache(self._cache, keys)
        if not exists:
            return True

        value.remove(tuple(policy))
        return True

    def __get_policy(self) -> Iterable[Sequence[str]]:
        if self._current_filter is not None:
            return (list(x) for x in self._current_filter)
        else:
            return (list(v2) for v in self._cache.values() for v1 in v.values() for v2 in v1)

    def apply_filter(self, *keys) -> None:
        _, value = in_cache(self._cache, keys)
        self._current_filter = value or set()

    def clear_filter(self) -> None:
        self._current_filter = None
