"""

"""

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches


def RotateTickLabels(fig):
    """
    Rotates all x-axis tick labels in seaborn facetgrid

    Parameters
    ----------
    fig : seaborn facetgrid
    """
    for axes in fig.axes.flat:
        _ = axes.set_xticklabels(axes.get_xticklabels(), rotation=90)


def plot_skills(player):
    # Plot skills on facetgrid (one skill per plot)
    skills_plot = sns.FacetGrid(data=player.skills, col='Skill', col_wrap=4,
                                sharey=False, height=3.5, aspect=1.5)
    skills_plot.map(sns.lineplot, 'Date', 'XP')
    # Add plot of level to XP plot using a 2nd y-axis
    for ax, (_, subdata) in zip(skills_plot.axes,
                                player.skills.groupby('Skill', sort=False)):
        ax2 = ax.twinx()
        subdata.plot(x='Date', y='Level', ax=ax2, legend=False, color='b')
        ax.set_ylabel('XP')
        ax2.set_ylabel('Level')

        # Create legend (colours obtained via plt.gca().lines[-1].get_color())
        name_to_color = {
            'XP': (0.8862745098039215, 0.2901960784313726, 0.2),
            'Level': 'b'
        }
        patches = [matplotlib.patches.Patch(
            color=v, label=k) for k, v in name_to_color.items()]
        plt.legend(handles=patches, loc='upper left')
    RotateTickLabels(skills_plot)
    plt.tight_layout()


def plot_killcount(player):
    killcount_plot = sns.FacetGrid(data=player.killcount, col='Boss',
                                   col_wrap=6, sharey=False)
    killcount_plot.map(sns.lineplot, 'Date', 'Kill count')
    RotateTickLabels(killcount_plot)
    plt.tight_layout()
