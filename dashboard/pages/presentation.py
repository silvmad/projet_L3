import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("présentation du projet", className="card-title"),
                html.P(
                    "Notre projet s'est porté sur l'observation et la detection de discurs de haine sur des réseaux sociaux et "
                    "plus particulièrement sur Twitter.",

                    className="card-text",
                ),
                html.P(
                    "Nous avons alors élaborer une suite d'outils afin de pouvoir collecter et analyser des messages en temps réel. "
                    "Cette collecte établie en fonction de mots clés "
                    "prédéfinis a servi à créer une représentation qualitative et quantitative du phénomène.",
                    className="card-text",
                    ),
                html.P(
                    "Ce projet s'articule autour de trois modules :", className="card-text", ),
                html.Br(),

                html.P(
                    "- La collecte de données :nous avons choisi d'observer Twitter au vu du volume des messages ce qui permet "
                    "de palier à toute distorsion de l'observation (automodération ou modération de la plateforme)",
                    className="card-text", ),
                html.P(
                    "- L'Analyse: les messages haineux seront distingués des messages non haineux et catégoriser en type de haine grace à une IA pattern matcher"
                    "fondé sur des regex",
                    className="card-text", ),

                html.P(
                    "- La présentation: via un dashboard permet une compéhension directe et rapide des résultats par n'importe quel utilisateur.",

                    className="card-text", ),

                html.P(
                    "L'objectif du projet est de faciliter l'accès aux données à l'aide d'une UI. Ceci afin de permettre son utilisation à un maximum d'utilisateur et ce, "
                    "quelque soit leur maitrise de l'outil informatique comme par exemple les étudiants en sociologie ou autres qui s'interesserait au phénomène de haine sur le net",

                    className="card-text", ),
                html.Br(),
                html.P(
                    "Vous pouvez contacter l'équipe via le mail suivant:",
                    className="card-text",
                ),
                dbc.CardFooter( children= (dbc.CardLink("dashboardhaine@gmail.com", href=""), ),),
            ],
            style={"width": "100%", "left": "50%", "margin-right": "30%","text-align": "justify", "text-justify": "inter-word"},
            ),
    ])

