from hypothesis import strategies as st

from engine.regex.ast import Concat, Empty, Epsilon, Node, Star, Symbol, Union


@st.composite
def regex_asts(draw, alphabet: str = "ab", max_depth: int = 4) -> Node:
    if max_depth <= 0:
        return draw(st.one_of(st.just(Empty()), st.just(Epsilon()), st.sampled_from(
            [Symbol(char) for char in alphabet]
        )))
    smaller = regex_asts(alphabet=alphabet, max_depth=max_depth - 1)
    return draw(
        st.one_of(
            st.just(Empty()),
            st.just(Epsilon()),
            st.sampled_from([Symbol(char) for char in alphabet]),
            smaller.map(Star),
            st.tuples(smaller, smaller).map(lambda pair: Union(*pair)),
            st.tuples(smaller, smaller).map(lambda pair: Concat(*pair)),
        )
    )
