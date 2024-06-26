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
        return plt.gca()
    return draw,


@app.cell
def __(draw, rr0):
    draw(rr0)
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
def __(RenderResult, dataclass):
    """Some common code, used in both implementations."""

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
def __(mo):
    mo.md(
        r"""
        ## Layering nodes
        """
    )
    return


@app.cell
def __(mo):
    render_width = mo.ui.number(start=1, stop=20, value=5, label="Render width")
    return render_width,


@app.cell
def __(mo, render_width):
    mo.hstack([render_width])
    return


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
def __(Callable, RenderResult, RenderStep, find_previous):
    def build_with(rr: RenderResult, fn: Callable[[RenderStep], RenderStep], width) -> RenderStep:
        step = RenderStep(rr, list(rr.roots), [], find_previous(rr))
        while step.roots:
            step = fn(step, width)
        return step
    return build_with,


@app.cell
def __(mo, render_width):
    mo.md(f"We use a `tube` algorithm to render graph with a maximum width of {render_width.value}.")
    return


@app.cell
def __(Dict, List, RenderResult, RenderStep, Set, add_if_not):
    def tube(step: RenderStep, width):
        new_layer: List[int] = []
        already_added: Set[int] = set(g for l in step.layers for g in l)
        for goal_id in step.roots:
            if len(new_layer) >= width:
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
def __(Dict, RenderResult, Set, render_width):
    def avg(vals):
        return sum(vals) / len(vals)

    def shift_neutral(ds):
        return avg([d[1] for d in ds])

    def calc_shift(rr: RenderResult, shift_fn):
        connected: Dict[int, Set[int]] = {row.goal_id: set() for row in rr.rows}
        for row in rr.rows:
            for e in row.edges:
                connected[e[0]].add(row.goal_id)
                connected[row.goal_id].add(e[0])

        result = {}
        for row in rr.rows:
            goal_id = row.goal_id
            opts = rr.node_opts[goal_id]
            row_, col_ = opts['row'], opts['col']
            deltas = [
                (rr.node_opts[c]['row'] - row_,
                 rr.node_opts[c]['col'] - col_)
                for c in connected[goal_id]
            ]
            result[goal_id] = shift_fn(deltas)
        return result

    def adjust_horisontal(rr: RenderResult, mult):
        deltas = calc_shift(rr, shift_neutral)
        new_opts = {
            goal_id: opts | {"col": opts["col"] + (mult * deltas[goal_id])}
            for goal_id, opts in rr.node_opts.items()
        }
        return RenderResult(
            rr.rows,
            node_opts=new_opts,
            select=rr.select,
            roots=rr.roots
        )

    def normalize_cols(rr: RenderResult) -> RenderResult:
        order0 = {}
        for goal_id, opts in rr.node_opts.items():
            row, col = opts["row"], opts["col"]
            if row not in order0:
                order0[row] = []
            order0[row].append((col, goal_id))
        # print("order0: ", order0)
        order1 = {}
        for layer, tuples in order0.items():
            non_empty = list(round(t[0]) for t in tuples)
            need_drop = len(tuples) - len(set(non_empty))
            empty = {x for x in range(render_width.value)}.difference(non_empty)
            for i in range(need_drop):
                empty.pop()
            # print(f"{layer}: non-empty {non_empty}, empty {empty}, dropped {need_drop}")
            order1[layer] = tuples + [(e, -10) for e in empty]
        # print("order1: ", order1)
        order2 = {k: sorted(v) for k, v in order1.items()}
        # print("order2: ", order2)
        indexed0 = {k: [t[1] for t in v] for k, v in order2.items()}
        # print("indexed0: ", indexed0)
        indexed1 = {}
        for layer in indexed0.values():
            for i, goal_id in enumerate(layer):
                if goal_id > 0:
                    indexed1[goal_id] = i
        # print("indexed1: ", indexed1)
        new_opts = {
            goal_id: opts | {"col": indexed1[goal_id]}
            for goal_id, opts in rr.node_opts.items()
        }
        # print(new_opts)
        return RenderResult(
            rr.rows,
            node_opts=new_opts,
            select=rr.select,
            roots=rr.roots
        )
    return adjust_horisontal, avg, calc_shift, normalize_cols, shift_neutral


@app.cell
def __(RenderResult, adjust_horisontal, normalize_cols):
    def tweak_horizontal(rr: RenderResult):
        r1 = adjust_horisontal(rr, 1.0)
        r2 = adjust_horisontal(r1, 0.5)
        r3 = normalize_cols(r2)
        return r3
    return tweak_horizontal,


@app.cell
def __(build_with, draw, render_width, rr0, tube):
    r1 = build_with(rr0, tube, render_width.value)

    draw(r1.rr)
    return r1,


@app.cell
def __(mo):
    mo.md("After horizontal tweaking...")
    return


@app.cell
def __(draw, r1, tweak_horizontal):
    draw(tweak_horizontal(r1.rr))
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
        This part does not introduce new steps to algorithm. Instead, it changes the format of notebook used. We expect to gain new _interactivity_ features from this approach. Therefore, some new steps in this direction should be done next.

        1. Try **interactivity** features. It may include, probably, something from the following list:
            1. Extract more algorithm variables into playbook levelm in addition to `WIDTH`, if possible.
            2. Use **feature flags** to switch between new and old logic. These flags could be moved up to UI level, and we would be able to switch them on and off.
            3. Exploit [code editor](https://docs.marimo.io/api/inputs/code_editor.html) functionality to keep a current state of the rendering function. We would be able to edit and execute it instantly, right?
            4. Probably, more.
        2. **Fake goals**. In order to draw edges properly, we need to add "fake goals" (intersection points between edge and current layer). Current version of algorithm knows nothing about it.
        3. **Multiple roots**. We need to re-check algorithm for graph containing multiple root nodes. We could have either several not-connected sub-graphs (a result of filtering, for example), or sub-graphs that have some intermediate connections between them. Probably, an energy-based logic would be more useful here. Nevertheless, we _may have_ to modify an existing `energy` function in a way that only the shortest edge is considered.
        4. **Performance**. There's still a room for improvement. It's not cool to have things like `new_opts = {... for goal_id, opts in step.rr.node_opts.items()`. We visit literally all nodes in `rr` while update only some of them. This place (and, probably, several others) should be reviewed and rewritten.
        """
    )
    return


@app.cell
def __():
    import marimo as mo
    return mo,


if __name__ == "__main__":
    app.run()
