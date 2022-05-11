"""

"""

from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.graph_objects as go


def create_summary_plots(player):
    # Create interactive plots of overall level/XP and total boss kill count
    # Note that this plot will open in the default browser
    overall_plot = make_subplots(rows=2, cols=2,
                                 vertical_spacing=0.2,
                                 specs=[[{}, {}],
                                        [{"colspan": 2}, None]])
    overall_plot.append_trace(go.Scatter(x=player.skills[(player.skills['Skill'] ==
                                                          'Overall')]['Date'],
                                         y=player.skills[(player.skills['Skill'] ==
                                                          'Overall')]['Level'],
                                         name='Level', mode='lines'),
                              row=1, col=1)
    overall_plot.append_trace(go.Scatter(x=player.skills[(player.skills['Skill'] ==
                                                          'Overall')]['Date'],
                                         y=player.skills[(player.skills['Skill'] ==
                                                          'Overall')]['XP'],
                                         name='XP', mode='lines'),
                              row=1, col=2)
    overall_plot.append_trace(go.Scatter(x=player.total_killcount['Date'],
                                         y=player.total_killcount['Kill count'],
                                         name='Kill count', mode='lines'),
                              row=2, col=1)
    overall_plot.update_xaxes(title_text='Date', row=1, col=1)
    overall_plot.update_xaxes(title_text='Date', row=1, col=2)
    overall_plot.update_xaxes(title_text='Date', row=2, col=1)
    overall_plot.update_yaxes(title_text='Total level', row=1, col=1)
    overall_plot.update_yaxes(title_text='Total XP', row=1, col=2)
    overall_plot.update_yaxes(title_text='Total boss kill count', row=2, col=1)
    overall_plot.update_layout(title_text='Overall stats')
    plot(overall_plot, auto_open=True, filename='overall_stats.html')
