def finanzas_bg(self, code: str):
        app = DjangoDash(
                name = code,
                external_stylesheets = EXTERNAL_STYLESHEETS,
                external_scripts = EXTERNAL_SCRIPTS,
        )
        dataframe = APIConnector( ip = self.ip, token = self.token).send_get_dataframe(
                    endpoint="nsp_etl_situacion_financiera",
                    params=None
        )
        bg_df = transform_nsp_etl_situacion_financiera(df=dataframe)
        #bg_df.to_parquet("finanzas.parquet")
        formato = bg_df['formato'].unique()
        height_layout = 380
        app.layout =  \
        Content([
            html.Div([dmc.Modal(title = '', id = f"modal_{i}", fullScreen=True, zIndex=10000, size= "85%" )for i in ['activo_graph','pasivo_graph','fondo_maniobra_graph']]),
            Grid([
                Col([
                    dmc.Title("Balance General")
                ],size= 3),
                Col([
                    dmc.Select(
                        label="Formato",
                        placeholder="Todos",
                        id="select-format",
                        value = formato[0],
                        data= formato,
                        clearable=False
                    )
                ],size= 2),
                Col([
                    dmc.Select(
                        label="Año",
                        placeholder="Todos",
                        id="select-year",
                        value = None,
                        data= [],
                        clearable=True
                    )
                ],size= 2),
               
                Col([
                    dmc.Select(
                        label="Trimestre",
                        placeholder="Todos",
                        id="select-quarter",
                        value = None,
                        data= [],
                        clearable=True
                    )
                ],size= 2),
                Col([
                    dmc.Select(
                        label="Mes",
                        placeholder="Todos",
                        id="select-month",
                        value = None,
                        data= [],
                        clearable=True
                    )
                ],size= 1),
                Col([
                    dmc.Select(
                        label="Moneda",
                        #placeholder="Todos",
                        id="select-coin",
                        value = "USD",
                        data= ["USD","PEN"],
                        clearable=True
                    )
                ],size= 1),
                Col([
                    darkModeToggleDash()
                ],size= 1),
                Col([
                    cardGraph(id="activo_graph")
                    #card_id(id_ = "activo_graph",title="ACTIVO",height=height_layout)
                ],size= 6),
                Col([
                    cardGraph(id="pasivo_graph")
                    #card_id(id_ = "pasivo_graph",title="PASIVO",height=height_layout)
                ],size= 6),
                Col([
                    cardGraph(id="fondo_maniobra_graph")
                    #card_id(id_ = "fondo_maniobra_graph",title="FONDO DE MANIOBRA",height=height_layout)
                ],size= 12),
               
            ]),
            html.Div(id='notifications-update-data'),
            dcc.Store(id='data-values'),
           
           
        ])
 


class FinanzasBap(LoginRequiredMixin,View):
    login_url = reverse_lazy('login')
    def get(self,request):
        code = str(uuid.uuid4())
        profile = Profile.objects.get(user_id = self.request.user.id)
 
        #print(profile.company.avatar_profile)
        context = {
            'dashboard': finanzas_balance_ap(code = code), #hacer q me pida el dataframe
            'code': code
        }
        return render(request,'comercial.html',context)
 