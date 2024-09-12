from django_plotly_dash import DjangoDash
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
import dash
from tasks.models import Phase, Cost, User, Project
from datetime import datetime
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc

def cardGraph(id = ''):
        return html.Div([
            dmc.LoadingOverlay(
                loaderProps={"variant": "bars", "color": "#01414b", "size": "xl"},
                loader=dmc.Image(src="https://i.imgur.com/KIj15up.gif", alt="", caption="", width=70,height=70),
                children=[
                    dmc.Card(
                        children=[
                            dmc.ActionIcon(
                                DashIconify(icon=f"feather:{"maximize"}"), 
                                color="blue", 
                                variant="default",
                                id=f"maxi{id}",
                                n_clicks=0,
                                mb=10,
                                style={'position': 'absolute','top': '4px','right': '4px','z-index': '99'},
                            ),
                            dcc.Graph(id=id)# figure=graph_empty
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        p=0
                    ),
                ]
            ),

        ])



def funcionDashPrueba(code: str, df_projects: dict):
    app = DjangoDash(name=code)

    # Convertir la lista de proyectos a un DataFrame
    df_projects = pd.DataFrame(df_projects)

    # Asegurarse de que las fechas están en formato datetime
    df_projects['start_date'] = pd.to_datetime(df_projects['start_date'])
    df_projects['end_date'] = pd.to_datetime(df_projects['end_date'])

    # Obtener las fases y costos para calcular KPIs
    project_ids = df_projects['id'].tolist()
    phases = Phase.objects.filter(project_id__in=project_ids)
    df_phases = pd.DataFrame(list(phases.values()))
    print(df_phases)

    costs = Cost.objects.filter(project_id__in=project_ids)
    df_costs = pd.DataFrame(list(costs.values()))

    # Asegurarse de que las fechas de fases y costos están en formato datetime
    df_phases.loc[:, 'start_date'] = pd.to_datetime(df_phases['start_date'])
    df_phases.loc[:, 'end_date'] = pd.to_datetime(df_phases['end_date'])
    df_costs.loc[:, 'date'] = pd.to_datetime(df_costs['date'])

    # Cálculos y KPIs
    df_phases.loc[:, 'weighted_progress'] = df_phases['percentage_completed'] * df_phases['duration_hours']
    
    project_progress = df_phases.groupby('project_id').apply(
        lambda x: x['weighted_progress'].sum() / x['duration_hours'].sum() if x['duration_hours'].sum() > 0 else 0
    ).reset_index(name='total_progress')

    # Calcular 'budget_used' para cada proyecto
    project_budget_used = df_costs.groupby('project_id').agg(
        budget_used=pd.NamedAgg(column='amount', aggfunc='sum')
    ).reset_index()

    # Calcular 'pending_tasks' para cada proyecto
    pending_tasks = df_phases[df_phases['status'] != 'completed'].groupby('project_id').size().reset_index(name='pending_tasks')

    # Unir todos los datos al DataFrame de proyectos
    df_projects = df_projects.merge(project_progress, left_on='id', right_on='project_id', how='left')
    df_projects = df_projects.merge(project_budget_used, left_on='id', right_on='project_id', how='left')
    df_projects = df_projects.merge(pending_tasks, left_on='id', right_on='project_id', how='left')

    # Crear un diccionario de mapeo de project_id a nombre de proyecto
    project_names = dict(Project.objects.filter(id__in=df_phases['project_id'].unique()).values_list('id', 'name'))
    # Agregar una nueva columna 'project_name' a df_phases
    df_phases.loc[:, 'project_name'] = df_phases['project_id'].map(project_names)


    # Reemplazar NaN por valores por defecto
    df_projects.loc[:, 'total_progress'] = df_projects['total_progress'].fillna(0)
    df_projects.loc[:, 'budget_used'] = df_projects['budget_used'].fillna(0)
    df_projects.loc[:, 'pending_tasks'] = df_projects['pending_tasks'].fillna(0)
    df_projects.loc[:, 'budget_remaining'] = df_projects['total_budget'] - df_projects['budget_used']
    # Calcula el tiempo restante en días
    df_projects.loc[:, 'time_remaining'] = (df_projects['end_date'] - pd.to_datetime(datetime.today())).dt.days
    
    # Layout de la aplicación
    app.layout = dbc.Container(
        children=[
        dmc.Title('Dashboard de Gestión de Proyectos', style={'text-align': 'center'}, size='h1'),

        html.Div(
                    style={
                        'padding': '20px',
                    }
                ),
                
        # Card general que contiene el selector de usuarios y dos gráficos
            dmc.Card(
                children=[
                    dmc.MultiSelect(
                        id='project-dropdown',
                        data=[
                            {'label': row['name'], 'value': row['id']} for _, row in df_projects.iterrows()
                        ],
                        value=df_projects['id'].tolist(),  # Selecciona todos por defecto
                        clearable=True,
                        label="Selecciona uno o más proyectos",
                        nothingFound="No existen usuarios",
                        style={'width': '80%', 'margin': '0 auto', 'padding': '20px'}
                    ),
                    # KPIs 1
                    html.Div(
                        id='kpis-container1',
                        style={
                            'display': 'flex', 
                            'justify-content': 'space-around', 
                            'padding': '20px',
                            'transition': 'all 0.5s ease-in-out'  # Efecto de transición suave
                        }
                    ),
                    
                ],
                withBorder=True,
                shadow="sm",
                radius="md",
                p=0
            ),
        
        dmc.Card(
            children=[
                dmc.CardSection(
                     # KPIs 2
                    html.Div(
                        id='kpis-container2',
                        style={
                            'display': 'flex', 
                            'justify-content': 'space-around', 
                            'padding': '20px',
                            'transition': 'all 0.5s ease-in-out'  # Efecto de transición suave
                        }
                    ),
                )      
            ],
            withBorder=True,
                shadow="sm",
                radius="md",
                p=0
        ),
            
        html.Div(
                    style={
                        'padding': '20px',
                    }
                ),
        
        # Gráficos
        dmc.Grid(
            children=[
                dmc.Col(cardGraph('progress-bar-chart'), span=6),
                dmc.Col(cardGraph('budget-pie-chart'), span=6),
            ],
            gutter="xl",
        ),

        html.Div(
                    style={
                        'padding': '20px',
                    }
                ),

        dmc.Card(
            children=[
                dmc.CardSection(
                     html.Div(id='project-summary-container')
                )      
            ],
            withBorder=True,
                shadow="sm",
                radius="md",
                p=0
        ),

        html.Div(
                    style={
                        'padding': '20px',
                    }
                ),

    ])

    # Callback para actualizar KPIs y gráficos
    @app.callback(
        [Output('kpis-container1', 'children'),
         Output('kpis-container2', 'children'),
         Output('progress-bar-chart', 'figure'),
         Output('budget-pie-chart', 'figure'),
         Output('project-summary-container', 'children'),
         ],
        [Input('project-dropdown', 'value'),]
    )

    def update_dashboard(selected_project_ids):
        if not selected_project_ids:
            return [
                html.Div("No hay proyectos o usuarios seleccionados.", style={'color': 'red'}),
                {}, {}, {}, {}, {}
            ]
        
        # Extraer los datos almacenados
        print(selected_project_ids)
        
        # Filtrar datos según proyectos seleccionados
        filtered_projects = df_projects.loc[df_projects['id'].isin(selected_project_ids)].copy()
        filtered_phases = df_phases.loc[df_phases['project_id'].isin(selected_project_ids)].copy()

        #print(filtered_projects)
        

        # Calcular KPIs agregados
        avg_progress = filtered_projects['total_progress'].mean()
        total_budget = filtered_projects['total_budget'].sum()
        total_budget_used = filtered_projects['budget_used'].sum()
        total_budget_remaining = filtered_projects['budget_remaining'].sum()
        total_pending_tasks = filtered_projects['pending_tasks'].sum()
        avg_time_remaining = filtered_projects['time_remaining'].mean()

        # Redondear el campo de progreso a dos decimales
        filtered_projects['total_progress'] = df_projects['total_progress'].round(2)

        # Formatear las fechas para que solo muestren la fecha sin las horas
        filtered_projects['start_date'] = df_projects['start_date'].dt.strftime('%Y-%m-%d')
        filtered_projects['end_date'] = df_projects['end_date'].dt.strftime('%Y-%m-%d')

        print(filtered_projects[['name', 'total_progress', 'start_date', 'end_date']])

        # Filtrar datos según proyectos seleccionados
        filtered_projects = df_projects[df_projects['id'].isin(selected_project_ids)].copy()

        # Calcular EV (Valor Ganado) y CPI
        filtered_projects['EV'] = (filtered_projects['total_progress'] / 100) * filtered_projects['total_budget']
        filtered_projects['CPI'] = filtered_projects['EV'] / filtered_projects['budget_used']

        # Semáforo de riesgo (según el valor del CPI)
        def get_risk_color(cpi):
            if cpi > 1:
                return 'green'
            elif 0.9 <= cpi <= 1:
                return 'orange'
            else:
                return 'red'

        # Crear KPIs incluyendo CPI
        avg_cpi = filtered_projects['CPI'].mean()

        # Semáforo de riesgo con CPI
        risk_lights = []
        for index, row in filtered_projects.iterrows():
            # Definir color basado en el valor de CPI
            if row['CPI'] >= 1:
                color = "green"
            elif 0.9 <= row['CPI'] < 1:
                color = "yellow"
            else:
                color = "red"
             # Añadir el div con el tooltip y el color basado en CPI
            risk_lights.append(
                html.Div(
                    dmc.Tooltip(
                        html.Div(
                            style={'width': '30px', 'height': '30px', 'border-radius': '50%', 'background-color': color},
                        ),
                        label=f"Proyecto: {row['name']} - CPI: {row['CPI']:.2f}",
                        position="top",
                        withArrow=True,
                        transition="fade",
                        transitionDuration=500,
                    ),
                    style={'display': 'inline-block', 'margin-right': '10px'}
                )
            )
        # Contenedor de los semáforos
        risk_light_container = html.Div(
            children=risk_lights,
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
        )   
      
        # Crear componentes de KPI 1
        kpis1 = [
            html.Div([
                html.H3(f"{avg_progress:.2f}%", style={'color': '#4CAF50'}),
                html.P("Progreso Promedio")
            ], className='kpi'),
            
            html.Div([
                html.H3(f"${total_budget_used:,.2f}", style={'color': '#2196F3'}),
                html.P("Presupuesto Usado")
            ], className='kpi'),
            
            html.Div([
                html.H3(f"${total_budget_remaining:,.2f}", style={'color': '#FFC107'}),
                html.P("Presupuesto Restante")
            ], className='kpi'),
            
            html.Div([
                html.H3(f"{int(avg_time_remaining)} días", style={'color': '#FF5722'}),
                html.P("Tiempo Promedio Restante")
            ], className='kpi'),
            
            html.Div([
                html.H3(f"{int(total_pending_tasks)}", style={'color': '#9C27B0'}),
                html.P("Tareas Pendientes")
            ], className='kpi'),
        ]

        # Crear componentes de KPI 2
        kpis2 = [
            html.Div([
            html.H3(f"CPI Promedio: {avg_cpi:.2f}", style={'color': '#FF5722'}),
            html.P("Índice de Desempeño de Costos (CPI)")
            ], className='kpi'),
        
            # Semáforo de riesgo
            html.Div(
            
                html.Div(risk_light_container, className="risk-semaphore"),
            
            style={'display': 'flex', 'justify-content': 'space-around', 'padding': '20px'}
            ),
        ]

        
        # Redondear el total_progress a dos decimales
        filtered_projects['total_progress'] = filtered_projects['total_progress'].astype(float).round(2)

        # Gráfico de barras simple de progreso por proyecto
        progress_bar_chart = px.bar(
            filtered_projects,
            x='name',
            y='total_progress',
            title='Progreso por Proyecto',
            labels={'name': 'Proyecto', 'total_progress': 'Progreso (%)'},
            color='name',  # Puedes quitar esta línea si no deseas colores por proyecto
            template='plotly_white'
        )

        progress_bar_chart.update_layout(
            xaxis_title="Proyectos",
            yaxis_title="Porcentaje de Progreso (%)",
            yaxis=dict(range=[0, 100]),
        )


     
        # Gráfico de pastel de distribución de presupuesto
        budget_pie_chart = px.pie(
            filtered_projects,
            names='name',
            values='total_budget',
            title='Distribución del Presupuesto por Proyecto',
            labels={'name': 'Proyecto', 'total_budget': 'Presupuesto'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        # Crear tabla de resumen del proyecto seleccionado
        project_summary_table = dash_table.DataTable(
            id='project-summary-table',
            columns=[
                {'name': 'Nombre del Proyecto', 'id': 'name'},
                #{'name': 'Descripción', 'id': 'description'},
                {'name': 'Presupuesto Total', 'id': 'total_budget'},
                {'name': 'Presupuesto Usado', 'id': 'budget_used'},
                {'name': 'Fecha de Inicio', 'id': 'start_date'},
                {'name': 'Fecha de Fin', 'id': 'end_date'},
                {'name': 'Progreso (%)', 'id': 'total_progress'}
            ],
            data=filtered_projects.to_dict('records'),
            style_cell={'textAlign': 'center', 'padding': '10px'},
            style_header={
                'backgroundColor': '#4CAF50',
                'fontWeight': 'bold',
                'color': 'white',
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'total_progress'},
                    'backgroundColor': 'rgba(76, 175, 80, 0.3)',
                    'color': 'black',
                }
            ],
        )
   
        return kpis1, kpis2, progress_bar_chart, budget_pie_chart, project_summary_table

    return app