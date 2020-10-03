from fastbin.policy import FilterablePolicy, filter_policy


class TestFilterablePolicy:
    def test_able_to_add_rules(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])

        assert list(policy) == [["sub", "obj", "read"]]

    def test_does_not_add_duplicates(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])
        policy.append(["sub", "obj", "read"])

        assert list(policy) == [["sub", "obj", "read"]]

    def test_can_remove_rules(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])
        policy.remove(["sub", "obj", "read"])

        assert list(policy) == []

    def test_returns_lengtt(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])

        assert len(policy) == 1

    def test_supports_in_keyword(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])

        assert ["sub", "obj", "read"] in policy

    def test_supports_filters(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])
        policy.append(["sub", "obj", "read2"])
        policy.append(["sub", "obj2", "read2"])

        policy.apply_filter("read2", "obj2")

        assert list(policy) == [["sub", "obj2", "read2"]]

    def test_clears_filters(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])
        policy.append(["sub", "obj", "read2"])
        policy.append(["sub", "obj2", "read2"])

        policy.apply_filter("read2", "obj2")
        policy.clear_filter()

        assert list(policy) == [
            ["sub", "obj", "read"],
            ["sub", "obj", "read2"],
            ["sub", "obj2", "read2"],
        ]


class TestContextManager:
    def test_filters_policy(self) -> None:
        policy = FilterablePolicy([2, 1])

        policy.append(["sub", "obj", "read"])
        policy.append(["sub", "obj", "read2"])
        policy.append(["sub", "obj2", "read2"])

        with filter_policy(policy, "read2", "obj2"):
            assert list(policy) == [["sub", "obj2", "read2"]]

        assert list(policy) == [
            ["sub", "obj", "read"],
            ["sub", "obj", "read2"],
            ["sub", "obj2", "read2"],
        ]
