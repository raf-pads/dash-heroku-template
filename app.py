#%%capture

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import dash_core_components as dcc
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#import plotly.offline as pyo 
#pyo.init_notebook_mode()


gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])


mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = 'Research has shown that working women are paid on average less than working men - this is what characterizes what has come to be known as the "gender wage gap". Research typically quantifies this gap as a woman making on average about 80 cents for every dollar a man makes. This difference can be attributed to differences in industries or jobs worked, as gender norms and expectations reinforce disparities between the sexes. However, when controlling for factors such as education and occupation for example, women cannot make up for this gender gap, which indicates that other underlying factors are at play in this inequity.'
markdown_text2 = 'The General Social Survey (GSS) studies the trends of American society by conducting personal interview surveys that are aimed at detecting social characteristics and attitudes in the U.S. population. It has been used for more than four decades and hundreds of trends have been tracked over these years. It is comprised of certain demographic, behavioral, and attitudinal questions with an addition of special topic questions such as morality, intergroup tolerance, and psychological wellbeing. The specific survey we are examining touches on one of these special interests - the social trends of females in the workforce. The NORC conducts these surveys through in-person interviews every other year and contacts those to participate through random selection.'

gss_display = gss_clean.groupby('sex', sort=False).agg({'sex':'size',
                                     'income':'mean',
                                    'job_prestige':'mean',
                                    'socioeconomic_index':'mean',
                                    'education':'mean'})

gss_display = gss_display[['income', 'job_prestige', 
                            'socioeconomic_index', 'education']]
gss_display = gss_display.rename({'sex':'Sex',
                                   'income':'Avg. Income',
                                   'job_prestige':'Avg. Occupational Prestige',
                                   'socioeconomic_index':'Avg. Socioeconomic Index',
                                   'education':'Avg. Years Education'}, axis=1)
gss_display = round(gss_display, 2)
gss_display = gss_display.reset_index().rename({'sex':'Sex'}, axis=1)
#gss_display
table = ff.create_table(gss_display)
table.show()


breadwinners = pd.crosstab(gss_clean.male_breadwinner, gss_clean.sex).reset_index()
breadwinners = pd.melt(breadwinners, id_vars = 'male_breadwinner', value_vars = ['male','female'])
breadwinners = breadwinners.rename({'value':'count'}, axis=1)

fig = px.bar(breadwinners, x='male_breadwinner', y='count', color='sex',
            labels={'male_breadwinner':'Male Breadwinner Response', 'count':'Count'},
            hover_data = ['count'],
            text='count',
            barmode = 'group')
fig.update_layout(showlegend=True)
fig.update(layout=dict(title=dict(x=0.5)))
fig.show()

gss_scatter = gss_clean[~gss_clean.sex.isnull()]


fig2 = px.scatter(gss_scatter, x='job_prestige', y='income', 
                 trendline='ols',
                 color = 'sex', 
                 height=600, width=600,
                 labels={'job_prestige':'Occupational Prestige', 
                        'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'])
fig2.update(layout=dict(title=dict(x=0.5)))
fig2.show()


fig3 = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Income', 'sex':''})
fig3.update_layout(showlegend=False)
fig3.update(layout=dict(title=dict(x=0.5)))
fig3.show()

fig4 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Occupational Prestige', 'sex':''})
fig4.update_layout(showlegend=False)
fig4.update(layout=dict(title=dict(x=0.5)))
fig4.show()

new_df = gss_clean[['income','sex','job_prestige']]

new_df['job_prestige_cat'] = pd.cut(new_df['job_prestige'], bins=6, labels=['1','2','3','4','5','6'])
new_df = new_df.sort_values(by = 'job_prestige_cat') 

clean_df = new_df.dropna(axis=0)

fig_bar = px.box(clean_df, x='sex', y='income', color='sex', 
             facet_col='job_prestige_cat', facet_col_wrap=2,
             hover_data = ['income'],
            labels={'sex':'Sex','income':'Income'},
            color_discrete_map = {'male':'blue', 'female':'red'},
            width=1000, height=600)
fig_bar.update(layout=dict(title=dict(x=0.5)))
fig_bar.update_layout(showlegend=False)
#fig_bar.for_each_annotation(lambda a: a.update(text=a.text.replace("vote=", "")))
fig_bar.show()


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring the GSS Survey Data"),
        
        dcc.Markdown(children = markdown_text),
        dcc.Markdown(children = markdown_text2),
        
        html.H5("Comparing Males and Females by Average Income, Average Occupational Prestige, Average Socioeconomic Status, and Average Years Education"),
        
        dcc.Graph(figure=table),
        
        html.H5("Assessing Level of Agreement between Males and Females on the Male Breadwinners"),
        
        dcc.Markdown(children = "Poll Question: It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family?"),
        
        dcc.Graph(figure=fig),
        
        html.H5("Income versus Occupational Prestige By Sex"),
        
        dcc.Graph(figure=fig2),
        
        html.Div([
            
            html.H5("Distribution of Income by Sex"),
            
            dcc.Graph(figure=fig3)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H5("Distribution of Occupational Prestige by Sex"),
            
            dcc.Graph(figure=fig4)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H5("Distribution of Income by Sex for each of the Job Prestige Levels"),
            
        dcc.Graph(figure=fig_bar)
    
    ]
)

if __name__ == '__main__':
    app.run_server(port = 5002)

   # debug=True, , use_reloader=False
