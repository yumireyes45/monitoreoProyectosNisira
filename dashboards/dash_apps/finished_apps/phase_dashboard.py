from django_plotly_dash import DjangoDash
from dash import html, dcc
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
import numpy as np

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


def funcionDash(code: str, df_projects: dict):
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

    users_in_phases = User.objects.filter(id__in=df_phases['user_id'].unique())
    df_users = pd.DataFrame(list(users_in_phases.values()))

    costs = Cost.objects.filter(project_id__in=project_ids)
    df_costs = pd.DataFrame(list(costs.values()))

    # Asegurarse de que las fechas de fases y costos están en formato datetime
    df_phases['start_date'] = pd.to_datetime(df_phases['start_date'])
    df_phases['end_date'] = pd.to_datetime(df_phases['end_date'])
    df_costs['date'] = pd.to_datetime(df_costs['date'])

    # Cálculos y KPIs
    df_phases['weighted_progress'] = df_phases['percentage_completed'] * df_phases['duration_hours']
    
    #project_progress = df_phases.groupby('project_id').apply(
    #    lambda x: x['weighted_progress'].sum() / x['duration_hours'].sum() if x['duration_hours'].sum() > 0 else 0
    #).reset_index(name='total_progress')

    # Calcular 'budget_used' para cada proyecto
    #project_budget_used = df_costs.groupby('project_id').agg(
    #    budget_used=pd.NamedAgg(column='amount', aggfunc='sum')
    #).reset_index()

    # Calcular 'pending_tasks' para cada proyecto
    pending_tasks = df_phases[df_phases['status'] != 'completed'].groupby('project_id').size().reset_index(name='pending_tasks')

    # Unir todos los datos al DataFrame de proyectos
    #df_projects = df_projects.merge(project_progress, left_on='id', right_on='project_id', how='left')
    #df_projects = df_projects.merge(project_budget_used, left_on='id', right_on='project_id', how='left')
    df_projects = df_projects.merge(pending_tasks, left_on='id', right_on='project_id', how='left')

    # Crear un diccionario que mapee user_id a username
    user_dict = dict(User.objects.values_list('id', 'username'))
    # Agregar la columna 'username' a df_phases
    df_phases['username'] = df_phases['user_id'].map(user_dict)

    # Crear un diccionario de mapeo de project_id a nombre de proyecto
    project_names = dict(Project.objects.filter(id__in=df_phases['project_id'].unique()).values_list('id', 'name'))
    # Agregar una nueva columna 'project_name' a df_phases
    df_phases['project_name'] = df_phases['project_id'].map(project_names)

    # Definir el diccionario de mapeo
    status_mapping = {
        "notcompleted": "No iniciado",
        "completed": "Completado",
        "progres": "En proceso"
    }
    # Mapear la columna 'status' con las etiquetas descriptivas
    df_phases['status'] = df_phases['status'].map(status_mapping)



    # Reemplazar NaN por valores por defecto
    #df_projects.loc[:, 'total_progress'] = df_projects['total_progress'].fillna(0)
    #df_projects.loc[:, 'budget_used'] = df_projects['budget_used'].fillna(0)
    df_projects['pending_tasks'] = df_projects['pending_tasks'].fillna(0)
    #df_projects.loc[:, 'budget_remaining'] = df_projects['total_budget'] - df_projects['budget_used']

    # Calcula el tiempo restante en días
    df_projects['time_remaining'] = (df_projects['end_date'] - pd.to_datetime(datetime.today())).dt.days

    # Calcular el trabajo restante real basado en el porcentaje completado
    df_phases['remaining_work'] = df_phases['duration_hours'] * (1 - df_phases['percentage_completed'] / 100)

    # KPI para horas restantes vs tareas completadas
    completed_tasks = df_phases[df_phases['status'] == 'Completado'].groupby('project_id').size().reset_index(name='completed_tasks')
    df_projects = df_projects.merge(completed_tasks, left_on='id', right_on='project_id', how='left') 

    # Cálculo de tareas totales por proyecto
    total_tasks = df_phases.groupby('project_id').size().reset_index(name='total_tasks')

    # Unir con df_projects
    df_projects = df_projects.merge(total_tasks, left_on='id', right_on='project_id', how='left')
    
    # Agrupar por proyecto para sumar las horas restantes
    hours_remaining = df_phases.groupby('project_id')['remaining_work'].sum().reset_index(name='hours_remaining')

    # Unir con df_projects, usando 'suffixes' para evitar conflictos de columnas
    df_projects = df_projects.merge(hours_remaining, left_on='id', right_on='project_id', how='left', suffixes=('', '_phases'))

    # Cálculo de la proporción de tareas completadas (completed_tasks / total_tasks)
    df_projects['completed_ratio'] = df_projects['completed_tasks'] / df_projects['total_tasks']


    # Imprimir df_projects para asegurarse de que no hay NaN
    print(df_projects['completed_tasks'])
    print(df_projects['total_tasks'])
    print(df_projects['hours_remaining'])
    print(df_projects['completed_ratio'])
    
    
    # Layout de la aplicación
    app.layout = html.Div(
        children=[
        dmc.Title('Dashboard de Gestión de Fases', style={'text-align': 'center'}, size='h1'),
        html.Div(
                    style={
                        'padding': '20px',
                    }
                ),
        # Card general que contiene el selector de proyectos, un html y dos gráficos
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
                # KPIs
                html.Div(
                    id='kpis-container',
                    style={
                        'display': 'flex', 
                        'justify-content': 'space-around', 
                        'padding': '20px',
                        'transition': 'all 0.5s ease-in-out'  # Efecto de transición suave
                    }
                ),

                # Insertar el semáforo de riesgo
                dmc.Card(
                    children=[
                        html.Div(id='kpis2-container', style={'text-align': 'center', 'padding': '20px'})
                    ],
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                ),

                dmc.Grid(
                    children=[
                        dmc.Col(cardGraph('timeline-chart'), span=6),
                        dmc.Col(cardGraph('tasks-bar-chart'), span=6),
                    ],
                    gutter="xl",
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(cardGraph('burndown_chart'), span=6),
                        dmc.Col(cardGraph('funnel_chart'), span=6),
                    ],
                    gutter="xl",
                ),
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


        # Card general que contiene el selector de usuarios y dos gráficos
        dmc.Card(
            children=[
                dmc.MultiSelect(
                    id='user-dropdown',
                    data=[{'label': row['username'], 'value': row['id']} for _, row in df_users.iterrows()],
                    value=df_users['id'].tolist(),  # Selecciona todos por defecto
                    clearable=True,
                    label="Selecciona uno o más usuarios",
                    nothingFound="No existen usuarios",
                    style={'width': '80%', 'margin': '0 auto', 'padding': '20px'}
                ),
                dmc.Grid(
                    children=[
                        dmc.Col(cardGraph('status-bar-chart'), span=6),
                        dmc.Col(cardGraph('comparison-timeline-chart'), span=6),
                    ],
                    gutter="xl",
                ),
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
        [Output('kpis-container', 'children'),
         Output('kpis2-container', 'children'),
         Output('timeline-chart', 'figure'),
         Output('tasks-bar-chart', 'figure'),
         Output('burndown_chart', 'figure'),
         Output('funnel_chart', 'figure'),
         Output('status-bar-chart', 'figure'),
         Output('comparison-timeline-chart', 'figure'),
         ],
        [Input('project-dropdown', 'value'),
         Input('user-dropdown', 'value')]
    )

    def update_dashboard(selected_project_ids, selected_user_ids):
        if not selected_project_ids:
            return [
                html.Div("No hay proyectos o usuarios seleccionados.", style={'color': 'red'}),
                {}, {}, {}, {}, {}
            ]
        
        
        
        # Filtrar datos según proyectos seleccionados
        filtered_projects = df_projects[df_projects['id'].isin(selected_project_ids)]
        filtered_phases = df_phases[df_phases['project_id'].isin(selected_project_ids)]
        filtered_costs = df_costs[df_costs['project_id'].isin(selected_project_ids)]

        print(filtered_projects)
        print(filtered_phases)
        
        

        # filtrar fases por usuarios seleccionados
        filtered_phases_user = df_phases[df_phases['user_id'].isin(selected_user_ids)]

        # Filtrar fases completadas y no completadas
        completed_phases = filtered_phases_user[filtered_phases_user['percentage_completed'] == 100]
        incomplete_phases = filtered_phases_user[filtered_phases_user['percentage_completed'] < 100]

        # Calcular número de fases completadas y no completadas
        num_completed_phases = len(completed_phases)
        num_incomplete_phases = len(incomplete_phases)
        #total_phases = num_completed_phases + num_incomplete_phases

        # Asegúrate de que total_phases no es cero para evitar divisiones por cero
        #if total_phases > 0:
        #    percent_completed_phases = (num_completed_phases / total_phases) * 100
        #    percent_incomplete_phases = (num_incomplete_phases / total_phases) * 100
        #else:
        #    percent_completed_phases = 0
        #    percent_incomplete_phases = 0

        # Calcular progreso en fases no completadas (teniendo en cuenta las horas pendientes)
        #incomplete_phases.loc[:, 'pending_hours'] = incomplete_phases['duration_hours'] * (1 - incomplete_phases['percentage_completed'] / 100)

        # Calcular KPIs agregados
        #avg_progress = filtered_projects['total_progress'].mean()
        #total_budget = filtered_projects['total_budget'].sum()
        #total_budget_used = filtered_projects['budget_used'].sum()
        #total_budget_remaining = filtered_projects['budget_remaining'].sum()
        total_pending_tasks = filtered_projects['pending_tasks'].sum()
        #avg_time_remaining = filtered_projects['time_remaining'].mean()

        # Generar fechas basadas en la duración de las fases
        df_burndown = filtered_phases.groupby('start_date').agg(
            {'remaining_work': 'sum'}
        ).sort_index().cumsum().reset_index()
        
        # Crear una columna para la línea de progreso ideal
        total_work = filtered_phases['duration_hours'].sum()
        df_burndown['ideal_work'] = np.linspace(total_work, 0, len(df_burndown))

        # Filtrar las fases completadas y agrupar por proyecto
        tasks_completed = filtered_phases[filtered_phases['status'] == 'Completado'].groupby('project_id').size().reset_index(name='completed_tasks')
        
        # Contar el total de fases por proyecto
        total_tasks = filtered_phases.groupby('project_id').size().reset_index(name='total_tasks')

        # Verifica si se están generando datos correctamente
        print(tasks_completed.head())
        print(total_tasks.head())

        # Unir ambas tablas en filtered_projects, asegurando que las columnas se generan correctamente
        filtered_projects = filtered_projects.merge(tasks_completed, on='project_id', how='left')
        filtered_projects = filtered_projects.merge(total_tasks, on='project_id', how='left')

        # Calcular el porcentaje de tareas completadas
        filtered_projects['tasks_completed'] = (filtered_projects['completed_ratio']) * 100


        filtered_projects['hours_remaining_percentage'] = filtered_projects['time_remaining'] / \
            (filtered_projects['end_date'] - filtered_projects['start_date']).dt.days * 100

        # Función para obtener el color del semáforo basado en el riesgo
        def calculate_risk_color(hours_remaining_percentage, tasks_completed):
            if tasks_completed > hours_remaining_percentage:
                return 'green'
            elif tasks_completed >= (hours_remaining_percentage * 0.9):
                return 'orange'
            else:
                return 'red'

        # Crear los indicadores de semáforo de riesgo
        risk_lights = []
        for index, row in filtered_projects.iterrows():
            # Obtener el color basado en la evaluación del riesgo
            color = calculate_risk_color(row['hours_remaining_percentage'], row['tasks_completed'])
            
            # Añadir el div con el semáforo de color y tooltip con la información del proyecto
            risk_lights.append(
                html.Div(
                    dmc.Tooltip(
                        html.Div(
                            style={'width': '30px', 'height': '30px', 'border-radius': '50%', 'background-color': color},
                        ),
                        label=f"Proyecto: {row['name']} - Progreso de Tareas: {row['tasks_completed']:.2f}% - Horas Restantes: {row['hours_remaining_percentage']:.2f}%",
                        position="top",
                        withArrow=True,
                        transition="fade",
                        transitionDuration=500,
                    ),
                    style={'display': 'inline-block', 'margin-right': '10px'}
                )
            )

        # Contenedor del semáforo
        risk_light_container = html.Div(
            children=risk_lights,
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
        )
         # Crear KPI de riesgo
        prom1 = filtered_projects['tasks_completed'].mean()
        prom2 = filtered_projects['hours_remaining_percentage'].mean()



      
        # Crear componentes de KPI
        kpis = [          
            html.Div([
                html.H3(f"{int(total_pending_tasks)}", style={'color': '#9C27B0', 'text-align': 'center'}),
                html.P("Tareas Pendientes")
            ], className='kpi'),
        ]

        kpis2 = [
            html.Div([
            html.H3(f"Tareas Completadas Promedio: {prom1:.2f}%", style={'color': '#FF5722'}),
            html.H3(f"Porcentaje de Horas Restantes: {prom2:.2f}%", style={'color': '#FF5722'}),
            html.P("Indicadores de Horas Restantes vs Tareas Completadas")
            ], className='kpi'),
        
            # Semáforo de riesgo
            html.Div(
            
                html.Div(risk_light_container, className="risk-semaphore"),
            
            style={'display': 'flex', 'justify-content': 'space-around', 'padding': '20px'}
            ),
        ]

        
        # Gráfico de línea de tiempo de fases
        if not filtered_phases.empty:

            # Agregar columna formateada para hover
            filtered_phases['importance'] = filtered_phases['important'].apply(lambda x: 'Importante' if x else 'No importante')

            timeline_chart = px.timeline(
                filtered_phases,
                x_start="start_date",
                x_end="end_date",
                y="name",
                color="status",
                title="Línea de Tiempo del Estado de las Fases",
                labels={'project_name':'Proyecto', 'status': 'Estado', 'start_date': 'Inicio'
                        , 'end_date': 'Fin', 'name': 'Fase', 'importance': 'Nivel'},
                hover_data=['project_name', 'importance']  # Agregar la importancia al hover]
            )
            timeline_chart.update_yaxes(autorange="reversed")  # Invertir el orden para mejor visualización
        else:
            timeline_chart = {}
        
        # Gráfico de tareas pendientes por usuario y tareas específicas
        if not filtered_phases.empty:
            # Filtrar solo las fases con tareas pendientes
            pending_phases = filtered_phases[filtered_phases['status'] != 'Completado']

            # Calcular las horas pendientes
            pending_phases['pending_hours'] = pending_phases['duration_hours'] * (1 - pending_phases['percentage_completed'] / 100)

            # Asegurarse de que 'pending_hours' sea numérico
            pending_hours = pending_phases['pending_hours'].astype(float).tolist()

             # Agregar la columna de importancia
            pending_phases['importance'] = pending_phases['important'].apply(lambda x: 'Importante' if x else 'No importante')


            tasks_scatter_plot = px.scatter(
                pending_phases,
                x='user_id',
                y='pending_hours',
                size=pending_hours,  # Tamaño del punto según la duración
                color='name',  # Color por nombre de la fase/tarea
                title='Fases Pendientes por Usuario',
                labels={'name': 'Fase Pendiente', 'user_id': 'Usuario', 'pending_hours': 'Horas Pendientes', 'importance': 'Nivel'},
                hover_data=['name', 'importance'],  # Agregar la importancia al hover
                color_discrete_sequence=px.colors.qualitative.Vivid
            )

            tasks_scatter_plot.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=pending_phases['user_id'].unique(),
                    ticktext=[User.objects.get(id=uid).username for uid in pending_phases['user_id'].unique()]
                )
            )
        else:
            tasks_scatter_plot = {}
        
        # Crear el Burndown Chart con tu data real
        burndown_chart = go.Figure()

        # Progreso Real
        burndown_chart.add_trace(go.Scatter(
            x=df_burndown['start_date'], 
            y=df_burndown['remaining_work'], 
            mode='lines+markers',
            name='Progreso Real',
            line=dict(color='red', width=2),
            hoverinfo='text',
            hovertext=[f'Día: {i}<br>Trabajo Restante: {r:.2f}' for i, r in zip(df_burndown['start_date'], df_burndown['remaining_work'])]
        ))

        # Línea Ideal
        burndown_chart.add_trace(go.Scatter(
            x=df_burndown['start_date'], 
            y=df_burndown['ideal_work'], 
            mode='lines',
            name='Progreso Ideal',
            line=dict(color='green', dash='dash', width=2),
            hoverinfo='text',
            hovertext=[f'Día Ideal: {i}<br>Trabajo Ideal Restante: {r:.2f}' for i, r in zip(df_burndown['start_date'], df_burndown['ideal_work'])]
        ))

        # Ajustes del layout
        burndown_chart.update_layout(
            title='Burndown Chart (Progreso Real vs Ideal)',
            xaxis_title='Fecha',
            yaxis_title='Trabajo Restante (Horas)',
            template='plotly_white',
            hovermode='x unified',
            annotations=[
                dict(x=df_burndown['start_date'].iloc[0], y=total_work, xref='x', yref='y', text='Inicio del Proyecto', showarrow=True, arrowhead=7),
                dict(x=df_burndown['start_date'].iloc[-1], y=0, xref='x', yref='y', text='Fin del Proyecto', showarrow=True, arrowhead=7)
            ],
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
        )

        # Agrupar fases por estado y contar el número de fases en cada uno
        phase_counts = filtered_phases['status'].value_counts().reset_index()
        phase_counts.columns = ['stage', 'number']

        # Crear el gráfico de funnel usando los datos de fases agrupados
        funnel_chart = px.funnel(
             phase_counts, 
             x='number', 
             y='stage', 
             title="Embudo de Fases por Estado",
             labels={'number': 'N° de Fases', 'stage': 'Estado'},
             )

        # Personalizar el estilo del gráfico
        funnel_chart.update_layout(
            template="plotly_white",
            xaxis_title="Número de Fases",
            yaxis_title="Estado"
        )


        # Crear gráfico de anillo
        status_pie_chart = go.Figure(
            data=[go.Pie(
                labels=["Completadas", "No Completadas"],
                values=[num_completed_phases, num_incomplete_phases],
                hole=.4,  # para hacer un gráfico de anillo
                hoverinfo='label+percent',
                textinfo='percent',
                marker=dict(colors=['#1052EA', '#CB1107'])  # colores opcionales
            )]
        )
        status_pie_chart.update_layout(
            title="Distribución de Fases Completadas vs No Completadas",
        )
        status_pie_chart.update_traces(
            pull=[0.1 if label == "No Completadas" else 0 for label in status_pie_chart.data[0]['labels']],
        )

        
        # Gráfico de línea de tiempo para comparar usuarios
        comparison_timeline_chart = px.timeline(
            filtered_phases_user,
            x_start="start_date",
            x_end="end_date",
            y="name",
            color="username",
            title="Comparación de Fases entre Usuarios",
            labels={'status': 'Estado','percentage_completed': '% Completado', 'user_id': 'Usuario', 'name': 'Fase', 
                    'username': 'Usuario', 'start_date': 'Inicio', 'end_date': 'Fin'},
            hover_data=['status', 'percentage_completed']
        )
        comparison_timeline_chart.update_yaxes(
             autorange="reversed",
             )  # Invertir el orden

        
        return kpis, kpis2, timeline_chart, tasks_scatter_plot, burndown_chart, funnel_chart, status_pie_chart, comparison_timeline_chart

    return app

