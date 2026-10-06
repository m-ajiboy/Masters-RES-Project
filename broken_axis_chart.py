"""Shared helper for re-plotting price charts that include AMIRIS's 3,000 EUR/MWh
shortage ceiling. A plain linear 0-3000+ y-axis squashes the 0-350 EUR/MWh range where
almost every real hour actually sits, so fine detail in ordinary-hour price movements
becomes invisible. This draws a BROKEN y-axis instead: a tall bottom panel covering the
readable range (-50 to 400 EUR/MWh, gridlines every 50 EUR/MWh, as requested) and a thin
top panel showing only the 3,000 EUR/MWh ceiling itself, joined by standard diagonal
break marks. When a series never actually reaches the ceiling, a plain single-panel chart
with the same fine 50-unit gridlines is used instead - no break is drawn where none is
needed.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BOTTOM_YLIM = (-50, 400)
BREAK_THRESHOLD = 600  # if nothing in any series exceeds this, skip the break entirely


def _series_max(series_dict):
    return max(float(max(y)) for _x, y in series_dict.values())


def plot_broken_price_chart(series_dict, styles, title, xlabel, ylabel, out_path,
                             note=None, legend_loc="upper right", figsize=(11, 7),
                             xtick_fn=None, shade=None, suptitle=None):
    """series_dict: {label: (x, y)}. styles: {label: dict of plot kwargs}.
    shade: optional (x0, x1, text) to draw a shaded vertical band (e.g. unresolved
    shortage hours) on the bottom panel, matching the original chart's convention."""
    needs_break = _series_max(series_dict) > BREAK_THRESHOLD

    if needs_break:
        fig, (ax_top, ax_bot) = plt.subplots(
            2, 1, figsize=figsize, sharex=True,
            gridspec_kw={"height_ratios": [1, 3.4], "hspace": 0.06},
        )
        for label, (x, y) in series_dict.items():
            ax_top.plot(x, y, label=label, **styles.get(label, {}))
            ax_bot.plot(x, y, label=label, **styles.get(label, {}))

        top_max = _series_max(series_dict)
        ax_top.set_ylim(top_max * 0.965, top_max * 1.04)
        ax_top.set_yticks([round(top_max / 100) * 100])
        ax_bot.set_ylim(*BOTTOM_YLIM)
        ax_bot.yaxis.set_major_locator(mticker.MultipleLocator(50))

        ax_top.spines["bottom"].set_visible(False)
        ax_bot.spines["top"].set_visible(False)
        ax_top.tick_params(labeltop=False, bottom=False)
        ax_bot.xaxis.tick_bottom()

        d = 0.012
        kwargs = dict(transform=ax_top.transAxes, color="k", clip_on=False, linewidth=1.2)
        ax_top.plot((-d, +d), (-d * 2.2, +d * 2.2), **kwargs)
        ax_top.plot((1 - d, 1 + d), (-d * 2.2, +d * 2.2), **kwargs)
        kwargs.update(transform=ax_bot.transAxes)
        ax_bot.plot((-d, +d), (1 - d * 0.8, 1 + d * 0.8), **kwargs)
        ax_bot.plot((1 - d, 1 + d), (1 - d * 0.8, 1 + d * 0.8), **kwargs)

        ax_top.grid(alpha=0.25)
        ax_bot.grid(alpha=0.35)
        ax_top.set_title(title, fontsize=13.5, fontweight="bold", pad=10)
        ax_bot.set_xlabel(xlabel, fontsize=10.5)
        ax_bot.set_ylabel(ylabel, fontsize=10.5)
        ax_top.set_ylabel(" ", fontsize=10.5)
        if shade is not None:
            x0, x1, text = shade
            ax_bot.axvspan(x0, x1, color="#888888", alpha=0.15)
            ax_bot.text((x0 + (x1 - x0) / 2) if not hasattr(x0, "timestamp") else x0, BOTTOM_YLIM[1] * 0.92,
                        text, ha="center", fontsize=8.5, color="#555555")
        ax_bot.legend(loc=legend_loc, fontsize=9.5, frameon=True)
        if xtick_fn is not None:
            xtick_fn(ax_bot)
        axes_for_note = ax_bot
        fig_for_save = fig
    else:
        fig, ax = plt.subplots(figsize=(figsize[0], figsize[1] * 0.72))
        for label, (x, y) in series_dict.items():
            ax.plot(x, y, label=label, **styles.get(label, {}))
        lo, hi = BOTTOM_YLIM
        data_max = _series_max(series_dict)
        hi = max(hi, (int(data_max / 50) + 2) * 50)
        ax.set_ylim(lo, hi)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(50))
        ax.grid(alpha=0.35)
        ax.set_title(title, fontsize=13.5, fontweight="bold", pad=10)
        ax.set_xlabel(xlabel, fontsize=10.5)
        ax.set_ylabel(ylabel, fontsize=10.5)
        if shade is not None:
            x0, x1, text = shade
            ax.axvspan(x0, x1, color="#888888", alpha=0.15)
            ax.text(x0, hi * 0.92, text, ha="center", fontsize=8.5, color="#555555")
        ax.legend(loc=legend_loc, fontsize=9.5, frameon=True)
        if xtick_fn is not None:
            xtick_fn(ax)
        axes_for_note = ax
        fig_for_save = fig

    if note:
        fig_for_save.text(0.5, 0.012, note, ha="center", fontsize=9, style="italic", color="#3a3a3a")
        plt.tight_layout(rect=[0, 0.035, 1, 1])
    else:
        plt.tight_layout()
    if suptitle:
        fig_for_save.suptitle(suptitle, fontsize=14.5, fontweight="bold", y=1.0)
        plt.tight_layout(rect=[0, 0.035 if note else 0, 1, 0.97])

    fig_for_save.savefig(out_path, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig_for_save)
    return needs_break
