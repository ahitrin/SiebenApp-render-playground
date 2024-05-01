import marimo

__generated_with = "0.4.7"
app = marimo.App()


@app.cell
def __(mo):
    mo.md(
        r"""
        # Part 12. Convert from `ipynb` to `marimo` notebook
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        **Motivation**: I'm not satisfied with the current level of interactivity provided by Jupyter Notebooks, so I want to try a new approach. `marimo` notebook framework claims that it provides a higher level of interactivity. Let's try it!
        """
    )
    return


@app.cell
def __(mo):
    mo.md("First, let's import a sample graph. It's not rendered properly yet.")
    return


@app.cell
def __():
    from siebenapp import RenderRow, RenderResult
    from sieben_example1 import EXAMPLE as rr0
    return RenderResult, RenderRow, rr0


@app.cell
def __():
    import matplotlib.pyplot as plt
    from dataclasses import dataclass
    from operator import itemgetter
    from random import randint
    from typing import Any, Callable, Union, Optional
    return (
        Any,
        Callable,
        Optional,
        Union,
        dataclass,
        itemgetter,
        plt,
        randint,
    )


@app.cell
def __(Dict, RenderResult, plt, randint):
    def draw(rr: RenderResult, min_row: int = 0) -> None:
        """Drawing function that also prints downgoing edges."""
        xpos: Dict[int, int] = {}
        ypos: Dict[int, int] = {}
        for goal_id, attrs in rr.goals():
            row, col = attrs.get("row", None), attrs.get("col", None)
            xpos[goal_id] = col if col is not None else randint(0, 10)
            ypos[goal_id] = row if row is not None else randint(min_row, 10) 
        for row in rr.rows:
            row_id = row.goal_id
            for edge in row.edges:
                e = edge[0]
                if ypos[row_id] > ypos[e]:
                    print(f"downgoing edge: {row_id}@{ypos[row_id]} -> {e}@{ypos[e]}")
                plt.plot([xpos[row_id], xpos[e]], [ypos[row_id], ypos[e]], 'ro-')
            plt.text(xpos[row_id] + 0.1, ypos[row_id], row.name)
        tops = [row.goal_id for row in rr.rows if row.is_switchable]
        plt.plot([xpos[t] for t in tops], [ypos[t] for t in tops], 'bo')
        plt.draw()
    return draw,


@app.cell
def __(draw, plt, rr0):
    draw(rr0)
    plt.gca()
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        A lot of downgoing edges, as expected. Nodes are placed at random, ignoring ordering.

        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Before cleanup
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        Some common code, used in both implementations.
        """
    )
    return


@app.cell
def __(RenderResult, dataclass):
    @dataclass
    class RenderStep:
        rr: RenderResult
        roots: list[int]
        layers: list[list[int]]
        previous: dict[int, list[int]]


    def pp(step: RenderStep):
        return [step.roots, step.layers]


    def add_if_not(m: dict, m1: dict) -> dict:
        nm = dict(m)
        for k, v in m1.items():
            if nm.get(k, None) is None:
                nm[k] = v
        return nm
    return RenderStep, add_if_not, pp


@app.cell
def __(RenderResult):
    def find_previous(rr: RenderResult) -> dict[int, list[int]]:
        result: dict[int, list[int]] = {g: [] for g in rr.roots}
        to_visit: set[int] = set(rr.roots)
        while to_visit:
            g = to_visit.pop()
            connections = [e[0] for e in rr.by_id(g).edges]
            for g1 in connections:
                to_visit.add(g1)
                result[g1] = result.get(g1, []) + [g]
        return result
    return find_previous,


@app.cell
def __():
    # Rendering defaults
    WIDTH = 5
    return WIDTH,


@app.cell
def __(mo):
    mo.md(
        r"""
        A previous version of `tube` function.
        """
    )
    return


@app.cell
def __(Dict, List, RenderResult, RenderStep, Set, WIDTH, add_if_not):
    def tube0(step: RenderStep):
        children_of_new_layer: Set[int] = set()
        new_layer: List[int] = []
        already_added: Set[int] = set(g for l in step.layers for g in l)
        for goal_id in step.roots:
            if len(new_layer) >= WIDTH:
                break
            if (goal_id not in children_of_new_layer) and \
                (all(g in already_added for g in step.previous[goal_id])):
                new_layer.append(goal_id)
                children_of_new_layer.update(e[0] for e in step.rr.by_id(goal_id).edges)
        new_roots: List[int] = step.roots[len(new_layer):] + \
                                [e[0] for gid in new_layer for e in step.rr.by_id(gid).edges]
        new_opts: Dict[int, Dict] = {
            goal_id: add_if_not(opts, {
                "row": len(step.layers) if goal_id in new_layer else None,
                "col": new_layer.index(goal_id) if goal_id in new_layer else None
            })
            for goal_id, opts in step.rr.node_opts.items()
        }
        new_layers = step.layers + [new_layer]
        already_added.update(set(g for l in new_layers for g in l))
        filtered_roots: List[int] = []
        for g in new_roots:
            if g not in already_added:
                filtered_roots.append(g)
                already_added.add(g)

        return RenderStep(
                RenderResult(step.rr.rows, node_opts=new_opts, select=step.rr.select, roots=step.rr.roots),
                filtered_roots,
                new_layers,
                step.previous)
    return tube0,


@app.cell
def __(mo):
    mo.md(
        r"""
        Run full render loop with an old function.
        """
    )
    return


@app.cell
def __(Callable, RenderResult, RenderStep, find_previous):
    def build_with(rr: RenderResult, fn: Callable[[RenderStep], RenderStep]) -> RenderStep:
        step = RenderStep(rr, list(rr.roots), [], find_previous(rr))
        while step.roots:
            step = fn(step)
        return step
    return build_with,


@app.cell
def __(build_with, pp, rr0, tube0):
    r0 = build_with(rr0, tube0)
    pp(r0)
    return r0,


@app.cell
def __(draw, r0):
    draw(r0.rr)
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        ## After cleanup
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        So, let's simply remove `children_of_new_layers` variable and everything that's related to it.
        """
    )
    return


@app.cell
def __(Dict, List, RenderResult, RenderStep, Set, WIDTH, add_if_not):
    def tube(step: RenderStep):
        new_layer: List[int] = []
        already_added: Set[int] = set(g for l in step.layers for g in l)
        for goal_id in step.roots:
            if len(new_layer) >= WIDTH:
                break
            if (all(g in already_added for g in step.previous[goal_id])):
                new_layer.append(goal_id)
        new_roots: List[int] = step.roots[len(new_layer):] + \
                                [e[0] for gid in new_layer for e in step.rr.by_id(gid).edges]
        new_opts: Dict[int, Dict] = {
            goal_id: add_if_not(opts, {
                "row": len(step.layers) if goal_id in new_layer else None,
                "col": new_layer.index(goal_id) if goal_id in new_layer else None
            })
            for goal_id, opts in step.rr.node_opts.items()
        }
        new_layers = step.layers + [new_layer]
        already_added.update(set(g for l in new_layers for g in l))
        filtered_roots: List[int] = []
        for g in new_roots:
            if g not in already_added:
                filtered_roots.append(g)
                already_added.add(g)

        return RenderStep(
                RenderResult(step.rr.rows, node_opts=new_opts, select=step.rr.select, roots=step.rr.roots),
                filtered_roots,
                new_layers,
                step.previous)
    return tube,


@app.cell
def __(build_with, pp, rr0, tube):
    r1 = build_with(rr0, tube)
    pp(r1)
    return r1,


@app.cell
def __(r0, r1):
    r0 == r1
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        Two results are really identical, that's good.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Next steps
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        What else could we improve? I have a hypothesis that we could use a kind of "virtual layers" when placing nodes. Instead of tracking and updating "previous" nodes, we could calculate "minimal virtual layer" for each of the node. Upon creating a `new_roots` variable, we sort ids by their virtual layers. When creating a `new_layer`, we take no more than `WIDTH` goals with the same virtual layer value. No need to track parents anymore.

        Having this idea in mind, and considering "backlog" from the previous part, we have the following items now:

        1. Try **virtual layers** instead of tracking "previous nodes".
        2. **Performance**. There's still a room for improvement. It's not cool to have things like `new_opts = {... for goal_id, opts in step.rr.node_opts.items()`. We visit literally all nodes in `rr` while update only some of them. This place (and, probably, several others) should be reviewed and rewritten.
        3. **Multiple roots**. We need to re-check algorithm for graph containing multiple root nodes. We could have either several not-connected sub-graphs (a result of filtering, for example), or sub-graphs that have some intermediate connections between them. Probably, an energy-based logic would be more useful here. Nevertheless, we _may have_ to modify an existing `energy` function in a way that only the shortest edge is considered.
        4. **Fake goals**. In order to draw edges properly, we need to add "fake goals" (intersection points between edge and current layer). Current version of algorithm knows nothing about it.
        5. **Horizontal adjustment tweaking**. It also _seems_ that the new generated graph could be additionally improved by horizontal adjustments. Is it true?
        """
    )
    return


@app.cell
def __():
    import marimo as mo
    return mo,


if __name__ == "__main__":
    app.run()
