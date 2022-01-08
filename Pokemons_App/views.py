from django.shortcuts import render
from .models import Pokemons
from django.db import connection

# Create your views here.


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def home(request):
    return render(request, 'home.html')


def add_a_pokemon(request):
    if request.method == 'POST' and request.POST:
        new_Name = request.POST["Name"]
        new_Type = request.POST["Type"]
        new_Generation = request.POST["Generation"]
        # new_Legendary = request.POST["Legendary"]
        new_Legendary = request.POST.get('Legendary', False)
        if new_Legendary == "on":
            new_Legendary = 1
        else:
            new_Legendary = 0
        new_HP = request.POST["HP"]
        new_Attack = request.POST["Attack"]
        new_Defense = request.POST["Defense"]

        new_pokemon = Pokemons(
            name=new_Name,
            type=new_Type,
            generation=new_Generation,
            legendary=new_Legendary,    # problem
            hp=new_HP,
            attack=new_Attack,
            defense=new_Defense)

        new_pokemon.save()
    return render(request, 'add_a_pokemon.html')


def query_results(request):
    with connection.cursor() as cursor:
        # Q1
        cursor.execute("""
                SELECT      P.Generation, P.Name
                FROM        Pokemons P
                            INNER JOIN (
                                SELECT P.Generation, MAX(P.Attack + P.Defense + P.HP) AS MaxTotal
                                FROM Pokemons P
                                GROUP BY P.Generation) MT
                            ON P.Generation = MT.Generation
                WHERE       (P.Legendary = 'true') AND (P.Attack + P.Defense + P.HP = MT.MaxTotal)
                ORDER BY    P.Generation
                """)
        sql_res1 = dictfetchall(cursor)

        # Q2
        cursor.execute("""
            Select P.Type, P.Name
            FROM Pokemons P
            EXCEPT (
                SELECT P1.Type, P1.Name
                FROM Pokemons P1 inner join Pokemons P2 on P1.Type= P2.Type
                WHERE P1.Name!= P2.Name and (P1.HP<= P2.HP or P1.Defense<= P2.Defense or P1.Attack<= P2.Attack)
            )
            ORDER BY Type
            ;
            """)
        sql_res2 = dictfetchall(cursor)

        # Q3
        if request.method == 'POST' and request.POST:
            my_attack_threshold = int(request.POST["attack_threshold"])
            my_pokemon_count = int(request.POST["pokemon_count"])
            cursor.execute("""
                        SELECT      P.Type
                        FROM        Pokemons P
                        WHERE       %s < ANY (
                                        SELECT P1.Attack
                                        FROM   Pokemons P1
                                        WHERE P1.Type = P.Type
                                        )
                                    AND
                                    %s < (
                                        SELECT COUNT(*) AS numPokemons
                                        FROM   Pokemons P2
                                        WHERE P2.Type = P.Type
                                        GROUP BY P2.Type
                                        )
                        GROUP BY P.Type
                        """, (my_attack_threshold, my_pokemon_count))
        sql_res3 = dictfetchall(cursor)

        # Q4
        cursor.execute("""
                SELECT m.type,m.maxUNSTABLE 
                FROM(
                SELECT ROUND(MAX(CAST(r.SumAbs as FLOAT)/CAST(r.typeCOUNTER as FLOAT)),2) as maxUNSTABLE
                FROM (
                Select Type, SUM(ABS(Attack-Defense)) as SumAbs, COUNT(Type) as typeCOUNTER
                FROM Pokemons
                GROUP BY(Type))as r) as n inner join (
                SELECT Type, ROUND(MAX(CAST(k.sumABS as FLOAT)/CAST(k.COUNTER as FLOAT)),2) as maxUNSTABLE
                FROM(
                SELECT h.Type, SUM(ABS) as sumABS, COUNT(Type) as COUNTER
                FROM(
                Select *, ABS(Attack-Defense) as ABS
                FROM Pokemons) as h
                GROUP BY Type )as k
                GROUP BY Type) as m on m.maxUNSTABLE=n.maxUNSTABLE;
                """)

        sql_res4 = dictfetchall(cursor)

    return render(request, 'query_results.html', {'sql_res1': sql_res1,
                                                  'sql_res2': sql_res2,
                                                  'sql_res3': sql_res3,
                                                  'sql_res4': sql_res4})
