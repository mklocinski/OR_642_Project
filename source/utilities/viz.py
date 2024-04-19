from datetime import datetime
from dash import dash_table
import pandas as pd
import plotly.express as px



def df_to_datatable(dataframe, editable=False):
    return dash_table.DataTable(
                data=dataframe.to_dict('records'),
                editable= editable,
                row_deletable= editable,
                columns=[{'name': i,
                          'id': i,
                          'deletable': editable,
                          'renamable': editable,} for i in dataframe.columns],
                page_size=10,
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                    'fontSize': '8pt',
                },
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in dataframe.to_dict('records')
                ],
                tooltip_duration=None,
            )

def format_model_output(model_output):
    formatted = model_output.drop_duplicates()
    formatted = formatted.sort_values(by=['Working Group', 'Start Time'],
                                      ascending=False)
    formatted['WG Label'] = [w.split()[0] for w in formatted['Working Group']]
    formatted['Start Time'] = [datetime.strptime(i, '%I:%M %p').time() if not pd.isna(i) else pd.NaT for i in
                               formatted['Start Time']]
    formatted['End Time'] = [datetime.strptime(i, '%I:%M %p').time() if not pd.isna(i) else pd.NaT for i in
                             formatted['End Time']]
    formatted['Date'] = [datetime.strptime(i, '%m/%d/%Y') if not pd.isna(i) else pd.NaT for i in formatted['Date']]
    formatted['Start Time'] = [datetime.combine(d, s) if not pd.isna(d) and not pd.isna(s) else pd.NaT for d, s in
                               zip(formatted['Date'], formatted['Start Time'])]
    formatted['End Time'] = [datetime.combine(d, s) if not pd.isna(d) and not pd.isna(s) else pd.NaT for d, s in
                             zip(formatted['Date'], formatted['End Time'])]

    return formatted


def filter_eval(filter_value):
    if filter_value is None:
        return False
    if type(filter_value) != list:
        return [filter_value]
    else:
        return filter_value


def reformat_date_string(date_string, in_format, out_format):
    string_date = datetime.strptime(date_string, in_format)
    return (datetime.strftime(string_date, out_format))


def string_to_datetime(date_string, type):
    if type == 'date':
        return datetime.strptime(date_string, "%Y-%m-%d")
    if type == 'time':
        return datetime.strptime(date_string, "%I:%M %p")
    if type == 'datetime':
        return datetime.strptime(date_string, "%Y-%m-%d %I:%M %p")
    else:
        return datetime.strptime(date_string, "%Y-%m-%d %I:%M %p")


def date_time_filter(data, column, filter_value, datetime_type):
    if not filter_value:
        return data
    if len(filter_value) == 1:
        return data[data[column] == string_to_datetime(filter_value[0], datetime_type)]
    else:
        return data[(data[column] >= string_to_datetime(filter_value[0], datetime_type)) & (
                data[column] <= string_to_datetime(filter_value[1], datetime_type))]


def string_filter(data, column, filter_value):
    if not filter_value:
        return data
    else:
        return data[data[column].isin(filter_value)]


def apply_filters(formatted_data, date_filter, wg_filter, author_filter):
    columns = {'Date': 'date', 'Working Group': 'string', 'Authors': 'string'}
    filters = [date_filter, wg_filter, author_filter]
    filtered_data = formatted_data
    for c, f in zip([i for i in columns.keys()], filters):
        if columns[c] in ('date', 'time', 'datetime'):
            filtered_data = date_time_filter(filtered_data, c, filter_eval(f), columns[c])
        else:
            filtered_data = string_filter(filtered_data, c, filter_eval(f))

    return filtered_data


def make_gantt(filtered_data):
    plot_df = filtered_data
    fig = px.timeline(plot_df,
                      x_start='Start Time',
                      x_end='End Time',
                      y='Presentation',
                      color='WG Label',
                      text='WG Label',
                      custom_data=[plot_df['Working Group'],
                                   plot_df['Authors'],
                                   [t.time().strftime("%I:%M %p") for t in plot_df['Start Time']],
                                   [t.time().strftime("%I:%M %p") for t in plot_df['End Time']]],
                      template="plotly_white")
    fig.update_xaxes(tickformat="%I:%M %p\n%A, %m/%d/%Y")
    fig.update_layout(uniformtext_minsize=8,
                      yaxis=dict(visible=False, showticklabels=False))
    fig.update_layout(showlegend=False)
    fig.update_traces(hovertemplate=
                      "<b>%{y}</b><br>" +
                      "<i>%{customdata[1]}</i><br>" +
                      "%{customdata[0]}<br><br>" +
                      "Start: %{customdata[2]}<br>" +
                      "End: %{customdata[3]}<br>" +
                      "<extra></extra>")

    return fig


def conflict_summary(model_output):
    total_presentations = len(set(model_output['Presentation']))
    total_authors = len(set(model_output['Authors']))
    total_wgs = len(set(model_output['Working Group']))
    double_booked_presentation = (model_output
                                     .groupby(['Presentation', 'Working Group', 'Date', 'Start Time'])
                                     .filter(lambda x: len(x) > 1)
                                     .filter(items=['Presentation'])
                                     .drop_duplicates())

    # more than one time scheduled for a set of authors?
    double_booked_authors = (model_output
                                .groupby(['Authors', 'Date', 'Start Time'])
                                .filter(lambda x: len(x) > 1)
                                .filter(items=['Authors'])
                                .drop_duplicates())

    # too many presentations in the same working group at the same time?
    overlapping_working_group = (model_output
                                    .groupby(['Working Group', 'Date', 'Start Time'])
                                    .filter(lambda x: len(x) > 1)
                                    .sort_values(by=['Working Group', 'Date', 'Start Time'])
                                    .filter(items=['Working Group'])
                                    .drop_duplicates())

    os_df = pd.DataFrame({'Evaluation': ['Double Booked Presentations',
                                     'Double Booked Authors',
                                     'Overlapping Working Groups'],
                       'Value': [len(double_booked_presentation),
                                 len(double_booked_authors),
                                 len(overlapping_working_group)],
                       'Population': [total_presentations, total_authors, total_wgs]
                       })

    return os_df, double_booked_presentation, double_booked_authors, overlapping_working_group

def plot_conflict_summary(output_summary):
    data = output_summary
    data['Conflicts'] = [round(v / p, 2) for v, p in zip(data['Value'], data['Population'])]
    data['No Conflicts'] = [1-c for c in data['Conflicts']]
    data = pd.melt(data, id_vars=["Evaluation", "Value", "Population"], value_vars=['Conflicts','No Conflicts'])
    data = data.rename(columns={'variable':'Result', 'value':"val"})
    fig = px.bar(data, y="Evaluation", x="val", color="Result", title="Output Evaluation",
                 orientation='h', text=data["val"].transform(lambda x: '{:,.0%}'.format(x)))
    fig.update_layout(yaxis_range=[0, 1])
    fig.update_yaxes(visible=False, showticklabels=False)
    return fig