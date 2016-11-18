# coding=utf8
import textwrap

import l20n.format.ast as FTL


def ftl(code):
    """Nicer indentation for FTL code.

    The code returned by this function is meant to be compared against the
    output of the FTL Serializer.  The input code will be UTF8-decoded and will
    end with a newline to match the output of the serializer.
    """

    # The FTL Serializer returns Unicode data so we use it as the baseline.
    code = code.decode('utf8')

    # The code might be triple-quoted.
    code = code.lstrip('\n')

    return textwrap.dedent(code)


def fold(fun, node, init):
    """Reduce `node` to a single value using `fun`.

    Apply `fun` against an accumulator and each subnode of `node` (in postorder
    traversal) to reduce it to a single value.
    """

    def fold_(vals, acc):
        if not vals:
            return acc

        head = vals[0]
        tail = vals[1:]

        if isinstance(head, FTL.Node):
            acc = fold(fun, head, acc)
        if isinstance(head, list):
            acc = fold_(head, acc)

        return fold_(tail, fun(acc, head))

    return fold_(vars(node).values(), init)
