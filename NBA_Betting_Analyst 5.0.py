import os
import time
import pandas as pd
from nba_api.stats.endpoints import commonteamroster, playergamelog, playercareerstats, leaguedashteamstats
from nba_api.stats.static import teams

def obter_ranking_defensivo():
    print("\n🛡️  Sincronizando estatísticas defensivas da liga...")
    stats_raw = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Base', season='2025-26').get_data_frames()[0]
    col_oponente = 'OPP_FG3_PCT' if 'OPP_FG3_PCT' in stats_raw.columns else 'FG3_PCT'
    ranking = stats_raw[['TEAM_NAME', col_oponente]].sort_values(by=col_oponente).reset_index(drop=True)
    ranking['RANK'] = ranking.index + 1
    return ranking.rename(columns={col_oponente: 'EFICIENCIA_DEF'})

def buscar_id_time(nome_digitado):
    todas_equipes = teams.get_teams()
    for t in todas_equipes:
        # Busca por parte do nome (ex: "Lakers" ou "Los Angeles")
        if nome_digitado.lower() in t['full_name'].lower():
            return t['id'], t['full_name']
    return None, None

def analisar_confronto_especifico():
    print("==============================================")
    print("🎯 ANALISADOR DE ODDS NBA - PLAYOFFS 2026")
    print("==============================================")
    
    # 1. Pergunta os times
    print("\nQual confronto você quer analisar hoje?")
    time_atk_input = input("Time do jogador (Ex: Lakers): ").strip()
    time_def_input = input("Time adversário (Ex: Rockets): ").strip()

    id_atk, nome_atk = buscar_id_time(time_atk_input)
    id_def, nome_def = buscar_id_time(time_def_input)

    if not id_atk or not id_def:
        print("❌ Não encontrei um dos times. Verifique o nome e tente novamente.")
        return

    ranking_def = obter_ranking_defensivo()
    
    # Pasta organizada pelo confronto
    pasta_nome = f"ANALISE_{nome_atk.replace(' ', '_')}_vs_{nome_def.replace(' ', '_')}"
    if not os.path.exists(pasta_nome): os.makedirs(pasta_nome)

    # Info da defesa oponente
    info_def = ranking_def[ranking_def['TEAM_NAME'] == nome_def].iloc[0]
    
    print(f"\n🔥 Iniciando análise: {nome_atk} atacando a defesa do {nome_def}...")
    print(f"📊 O {nome_def} é a {int(info_def['RANK'])}ª melhor defesa de 3 pontos.")

    # 2. Pega o Elenco do time de ataque
    roster = commonteamroster.CommonTeamRoster(team_id=id_atk, season='2025-26').get_data_frames()[0]

    for _, row in roster.iterrows():
        p_id, p_name = row['PLAYER_ID'], row['PLAYER']
        
        try:
            # Puxa logs
            log_p = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', season_type_all_star='Playoffs').get_data_frames()[0]
            log_r = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', season_type_all_star='Regular Season').get_data_frames()[0]
            
            logs_validos = [t for t in [log_p, log_r] if not t.empty]
            if not logs_validos: continue
            
            df_recent = pd.concat(logs_validos).head(5)
            m_3pm = df_recent['FG3M'].mean()
            m_3pa = df_recent['FG3A'].mean()

            # Filtro: Só analisa quem chuta pelo menos 2 vezes por jogo
            if m_3pa >= 2.0:
                filename = os.path.join(pasta_nome, f"{p_name.replace(' ', '_')}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"PROJEÇÃO DE APÓSTAS: {p_name.upper()}\n")
                    f.write(f"CONFRONTO: {nome_atk} vs {nome_def}\n")
                    f.write("="*70 + "\n\n")
                    
                    f.write(f"📈 PERFORMANCE RECENTE:\n")
                    f.write(f"Média Acertos (3PM): {m_3pm:.1f}\n")
                    f.write(f"Média Tentativas (3PA): {m_3pa:.1f}\n\n")
                    
                    f.write(f"🛡️ CONTEXTO ADVERSÁRIO:\n")
                    f.write(f"O {nome_def} permite {info_def['EFICIENCIA_DEF']*100:.1f}% de aproveitamento (Rank {int(info_def['RANK'])}).\n\n")

                    f.write(f"💡 VEREDITO:\n")
                    if info_def['RANK'] > 20 and m_3pa >= 5.5:
                        f.write("🔥 LUZ VERDE: Volume alto contra defesa fraca. Ótima chance de Over 1.5/2.5.\n")
                    elif info_def['RANK'] <= 8:
                        f.write("⚠️ CUIDADO: Defesa de elite. O aproveitamento pode cair drasticamente.\n")
                    elif m_3pm >= 2.0:
                        f.write("✅ CONSISTENTE: Tem mantido a média de 2 bolas convertidas.\n")
                    else:
                        f.write("⚖️ NEUTRO: Sem vantagem clara. Verifique a odd.\n")

            print(f"✅ Analisado: {p_name}")
            time.sleep(0.5)
        except:
            continue

    print(f"\n🚀 Tudo pronto! Arquivos gerados na pasta: {pasta_nome}")

if __name__ == "__main__":
    analisar_confronto_especifico()