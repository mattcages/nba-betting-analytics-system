import os
import time
import pandas as pd
from nba_api.stats.endpoints import playergamelog, leaguedashteamstats
from nba_api.stats.static import players, teams

def obter_ranking_defensivo():
    print("\n🛡️  Sincronizando defesas da liga...")
    try:
        stats_raw = leaguedashteamstats.LeagueDashTeamStats(measure_type_detailed_defense='Base', season='2025-26').get_data_frames()[0]
        col_oponente = 'OPP_FG3_PCT' if 'OPP_FG3_PCT' in stats_raw.columns else 'FG3_PCT'
        ranking = stats_raw[['TEAM_NAME', col_oponente]].sort_values(by=col_oponente).reset_index(drop=True)
        ranking['RANK'] = ranking.index + 1
        return ranking.rename(columns={col_oponente: 'EFICIENCIA_DEF'})
    except:
        return pd.DataFrame()

def buscar_player_id(nome):
    p_list = players.find_players_by_full_name(nome)
    if p_list: return p_list[0]['id'], p_list[0]['full_name']
    return None, None

def buscar_time_nome(termo):
    t_list = teams.get_teams()
    for t in t_list:
        if termo.lower() in t['full_name'].lower(): return t['full_name']
    return None

def analisar_individual_v4_plus():
    print("==============================================")
    print("🎯 ANALISADOR V4.1 - CRITÉRIO MÃO QUENTE")
    print("==============================================")

    nome_input = input("Jogador: ").strip()
    p_id, p_full_name = buscar_player_id(nome_input)
    if not p_id: return print("❌ Jogador não encontrado.")

    time_def_input = input(f"Contra quem o {p_full_name} joga? ").strip()
    nome_def = buscar_time_nome(time_def_input)
    if not nome_def: return print("❌ Time não encontrado.")

    mando = input("Local (1 para CASA / 2 para FORA): ").strip()
    linha_odd = float(input("Linha da aposta (Ex: 2.5): "))

    print(f"\n📊 Analisando {p_full_name}...")
    
    # Coleta de Dados
    log_p = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', season_type_all_star='Playoffs').get_data_frames()[0]
    log_r = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26', season_type_all_star='Regular Season').get_data_frames()[0]
    log_total = pd.concat([log_p, log_r])
    
    rank_def = obter_ranking_defensivo()
    info_def = rank_def[rank_def['TEAM_NAME'] == nome_def].iloc[0]

    # --- LÓGICA DE CÁLCULO ---
    
    # 1. Média Geral vs Média Curta (MÃO QUENTE)
    media_longa = log_total['FG3M'].mean()
    media_curta = log_total.head(3)['FG3M'].mean() # Últimos 3 jogos
    
    # 2. Home vs Away
    j_casa = log_total[log_total['MATCHUP'].str.contains('vs.')]
    j_fora = log_total[log_total['MATCHUP'].str.contains('@')]
    m_h_3pm = j_casa['FG3M'].mean() if not j_casa.empty else 0
    m_a_3pm = j_fora['FG3M'].mean() if not j_fora.empty else 0

    # 3. Volume Playoffs vs Regular
    m_3pa_reg = log_r['FG3A'].mean() if not log_r.empty else 0
    m_3pa_play = log_p['FG3A'].mean() if not log_p.empty else 0

    # --- APLICAÇÃO DOS CRITÉRIOS (SCORE) ---
    score = 0
    avisos = []

    # CRITÉRIO: Mão Quente
    if media_curta >= (media_longa * 1.20):
        score += 2
        avisos.append(f"🔥 MÃO QUENTE: {media_curta:.1f} acertos nos últimos 3 jogos (20%+ que a média).")
    elif media_curta <= (media_longa * 0.80):
        score -= 1
        avisos.append(f"❄️ FASE FRIA: Chute sumiu nos últimos jogos ({media_curta:.1f} acertos).")

    # CRITÉRIO: Sniper Confortável
    if mando == '1' and m_h_3pm > m_a_3pm:
        score += 1
        avisos.append(f"🏠 CASA: Rende mais no próprio ginásio ({m_h_3pm:.1f}).")
    elif mando == '2' and m_a_3pm >= m_h_3pm:
        score += 1
        avisos.append(f"✈️ FORA: Mantém o nível como visitante ({m_a_3pm:.1f}).")

    # CRITÉRIO: Volume de Playoffs
    diff_vol = m_3pa_play - m_3pa_reg
    if diff_vol >= 2.0:
        score += 3
        avisos.append(f"🧨 AGRESSIVO: Volume de chutes explodiu nos Playoffs (+{diff_vol:.1f}).")

    # Ajuste Final e Redutor de Defesa
    proj_final = media_curta # Baseamos a projeção no momento atual
    if int(info_def['RANK']) <= 5:
        proj_final *= 0.8
        avisos.append(f"🛡️ DEFESA ELITE: Redutor aplicado devido ao Rank {int(info_def['RANK'])} do adversário.")

    # --- RESULTADO NO TERMINAL ---
    print("\n" + "="*50)
    print(f"📋 RESULTADO PARA {p_full_name}")
    print("="*50)
    for a in avisos: print(f" [OK] {a}")
    
    print(f"\n🎯 Média Temporada: {media_longa:.1f} | Média Atual: {media_curta:.1f}")
    print(f"🚀 PROJEÇÃO AJUSTADA: {proj_final:.2f}")
    print(f"💎 SCORE FINAL: {score}/7")
    print("-" * 50)

    if score >= 5 and proj_final >= linha_odd:
        print("🍀 VEREDITO: LUZ VERDE MÁXIMA! Momento e cenário perfeitos.")
    elif proj_final >= linha_odd:
        print("✅ VEREDITO: VALOR POSITIVO. Bom para compor bilhete.")
    else:
        print("⚠️ VEREDITO: RISCO ALTO. Momento ruim ou defesa muito forte.")
    print("="*50)

if __name__ == "__main__":
    analisar_individual_v4_plus()