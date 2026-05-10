import os
import time
import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster, playergamelog, playercareerstats

def escanear_playoffs_2026():
    # Lista oficial dos times nos Playoffs de 2026
    times_playoffs = [
        "Oklahoma City Thunder", "San Antonio Spurs", "Denver Nuggets", 
        "Los Angeles Lakers", "Houston Rockets", "Minnesota Timberwolves", 
        "Portland Trail Blazers", "Phoenix Suns",
        "Detroit Pistons", "Boston Celtics", "New York Knicks", 
        "Cleveland Cavaliers", "Toronto Raptors", "Atlanta Hawks", 
        "Philadelphia 76ers", "Orlando Magic"
    ]

    root_folder = 'NBA_PLAYOFFS_2026'
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)

    all_nba_teams = teams.get_teams()
    
    # Filtra apenas os times da nossa lista
    lista_alvo = [t for t in all_nba_teams if t['full_name'] in times_playoffs]

    print(f"🚀 Iniciando varredura dos {len(lista_alvo)} times nos Playoffs...")

    for team in lista_alvo:
        team_name = team['full_name']
        team_id = str(team['id'])
        team_folder = os.path.join(root_folder, team_name.replace(' ', '_'))

        if not os.path.exists(team_folder):
            os.makedirs(team_folder)

        print(f"\n📂 Coletando: {team_name}...")

        try:
            roster = commonteamroster.CommonTeamRoster(team_id=team_id, season='2025-26').get_data_frames()[0]
            
            for _, row in roster.iterrows():
                p_id = row['PLAYER_ID']
                p_name = row['PLAYER']
                
                print(f"  > {p_name}")

                try:
                    # Puxa logs de Playoffs (Prioridade) e Regular
                    log_p = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', season_type_all_star='Playoffs').get_data_frames()[0]
                    log_r = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', season_type_all_star='Regular Season').get_data_frames()[0]
                    
                    # Une os logs para ter os 5 jogos mais recentes (incluindo ontem)
                    ultimos_5 = pd.concat([log_p, log_r]).head(5)
                    carreira = playercareerstats.PlayerCareerStats(player_id=p_id).get_data_frames()[0]

                    # Salva o relatório focado em 3 pontos para apostas
                    filename = os.path.join(team_folder, f"{p_name.replace(' ', '_')}.txt")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(f"ANÁLISE PLAYOFFS 2026 - {p_name.upper()}\n")
                        f.write("="*95 + "\n")
                        f.write("🎯 MÉTRICAS PARA 3 PONTOS (ÚLTIMOS 5 JOGOS):\n")
                        if not ultimos_5.empty:
                            cols = ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FG3M', 'FG3A', 'FG3_PCT', 'PTS']
                            f.write(ultimos_5[cols].to_string(index=False))
                        else:
                            f.write("Sem dados recentes nesta temporada.")
                        
                        f.write("\n\n" + "📈 HISTÓRICO GERAL (CARREIRA):\n")
                        f.write(carreira[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'FG3M', 'FG3A', 'FG3_PCT']].to_string(index=False))

                except Exception as e:
                    pass # Silencia erros individuais de jogadores para não travar o loop
                
                time.sleep(0.6) # Evita bloqueio da API

        except Exception as e:
            print(f"❌ Erro no time {team_name}: {e}")

    print("\n✅ BANCO DE DADOS DE PLAYOFFS ATUALIZADO!")

if __name__ == "__main__":
    escanear_playoffs_2026()