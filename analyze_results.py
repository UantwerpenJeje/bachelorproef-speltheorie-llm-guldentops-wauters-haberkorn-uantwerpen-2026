#!/usr/bin/env python3
"""Analyse LLM game-theory experiment results and save all figures to results/."""

import glob
import os
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings('ignore')

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')

# ── Reference values ──────────────────────────────────────────────────────────
HUMAN_COOP = {
    'prisoners_dilemma': 0.675,  # 60-75%, midpoint
    'chicken_game':      0.50,
    'stag_hunt':         0.60,
}
HUMAN_DICTATOR_SHARE = 28.0   # euros out of 100
HUMAN_BEAUTY_R1      = 36.0   # round-1 mean

# level-k thresholds (uniform prior on [0,100], target = 2/3)
LEVEL_K_THRESHOLDS = [(45, 0), (28, 1), (18, 2), (5, 3)]  # (lower-bound, level)

GAME_LABEL = {
    'prisoners_dilemma': "Prisoner's Dilemma",
    'chicken_game':      'Chicken Game',
    'stag_hunt':         'Stag Hunt',
}

MODEL_ORDER = [
    'gpt-4o-mini', 'claude-haiku', 'gemini-flash',
    'deepseek-chat', 'llama-3.1-8b', 'grok',
]
MODEL_COLORS = {
    'gpt-4o-mini':   '#4e79a7',
    'claude-haiku':  '#f28e2b',
    'gemini-flash':  '#59a14f',
    'deepseek-chat': '#e15759',
    'llama-3.1-8b':  '#76b7b2',
    'grok':          '#edc948',
}
SHORT_NAME = {
    'gpt-4o-mini':   'GPT-4o\nmini',
    'claude-haiku':  'Claude\nHaiku',
    'gemini-flash':  'Gemini\nFlash',
    'deepseek-chat': 'DeepSeek',
    'llama-3.1-8b':  'Llama\n3.1-8B',
    'grok':          'Grok',
}


# ── Data loading ──────────────────────────────────────────────────────────────

def load_data():
    all_csv = glob.glob(os.path.join(RESULTS_DIR, '*.csv'))

    iterative  = [f for f in all_csv
                  if os.path.basename(f).startswith('results_')
                  and 'llmvsllm' not in f
                  and 'oneshot'  not in f]
    llmvsllm   = [f for f in all_csv if 'llmvsllm'      in f]
    dictator   = [f for f in all_csv if 'dictator_game'  in f]
    beauty     = [f for f in all_csv if 'beauty_contest' in f]

    def concat(files):
        frames = [pd.read_csv(f) for f in files]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    return concat(iterative), concat(llmvsllm), concat(dictator), concat(beauty)


# ── Nash-deviation helper ─────────────────────────────────────────────────────

def _nash_dev(llm_act, opp_act, game):
    """1 = deviated from Nash, 0 = at Nash, NaN = undefined."""
    if game == 'prisoners_dilemma':
        # Dominant strategy: D.  Deviation = playing C.
        return 1 if llm_act == 'C' else 0
    if game == 'chicken_game':
        # Pure-strategy Nash: (C,D) and (D,C).
        return 0 if (llm_act, opp_act) in {('C', 'D'), ('D', 'C')} else 1
    if game == 'stag_hunt':
        # Nash equilibria: (C,C) and (D,D).
        return 0 if (llm_act, opp_act) in {('C', 'C'), ('D', 'D')} else 1
    return np.nan


def level_k(mean_val):
    for threshold, k in LEVEL_K_THRESHOLDS:
        if mean_val >= threshold:
            return k
    return 4  # Nash (≈0)


# ── Analysis functions ────────────────────────────────────────────────────────

def analyze_iterative(df):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = df.copy()
    df['coop']     = (df['llm_action'] == 'C').astype(float)
    df['nash_dev'] = df.apply(
        lambda r: _nash_dev(r['llm_action'], r['opponent_action'], r['game']),
        axis=1,
    )

    grp_cols = ['model', 'game', 'opponent_strategy', 'framing', 'temperature']
    agg = (
        df.groupby(grp_cols)
        .agg(
            coop_rate=    ('coop',      'mean'),
            nash_dev_rate=('nash_dev',  'mean'),
            payoff_mean=  ('llm_payoff','mean'),
            payoff_std=   ('llm_payoff','std'),
            n_rounds=     ('coop',      'count'),
        )
        .reset_index()
    )

    # Framing effect (neutral − competitive) per model × game × opponent × temp
    pivot = agg.pivot_table(
        index=['model', 'game', 'opponent_strategy', 'temperature'],
        columns='framing',
        values='coop_rate',
    ).reset_index()
    if 'neutral' in pivot.columns and 'competitive' in pivot.columns:
        pivot['framing_effect'] = pivot['neutral'] - pivot['competitive']

    return agg, pivot


def analyze_dictator(df):
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby(['model', 'framing', 'temperature'])
        .agg(
            mean_shared=('amount_shared', 'mean'),
            std_shared= ('amount_shared', 'std'),
            n=          ('amount_shared', 'count'),
        )
        .reset_index()
    )


def analyze_beauty(df):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    by_round = (
        df.groupby(['model', 'framing', 'temperature', 'round'])['llm_number']
        .agg(mean_number='mean', std_number='std', n='count')
        .reset_index()
    )

    overall = (
        df.groupby(['model', 'framing', 'temperature'])['llm_number']
        .agg(mean_number='mean', std_number='std')
        .reset_index()
    )
    overall['level_k'] = overall['mean_number'].apply(level_k)

    return by_round, overall


def analyze_llmvsllm(df):
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df['coop'] = (df['llm_action'] == 'C').astype(float)

    return (
        df.groupby(['model', 'opponent_model', 'game', 'framing', 'temperature'])
        .agg(
            coop_rate=  ('coop',       'mean'),
            payoff_mean=('llm_payoff', 'mean'),
            payoff_std= ('llm_payoff', 'std'),
            n=          ('coop',       'count'),
        )
        .reset_index()
    )


# ── Summary table ─────────────────────────────────────────────────────────────

def build_summary_table(iter_agg, dictator_agg, beauty_overall, llm_agg):
    rows = []
    games = ['prisoners_dilemma', 'chicken_game', 'stag_hunt']

    for model in MODEL_ORDER:
        row = {'model': model}

        # Iterative games
        for game in games:
            for temp in [0, 1]:
                sub = iter_agg[
                    (iter_agg['model'] == model) &
                    (iter_agg['game']  == game)  &
                    (iter_agg['temperature'] == temp)
                ]
                tag = f"{game[:2].upper()}_T{temp}"
                row[f'{tag}_coop']    = sub['coop_rate'].mean()    if not sub.empty else np.nan
                row[f'{tag}_nash_dev']= sub['nash_dev_rate'].mean() if not sub.empty else np.nan
                row[f'{tag}_payoff']  = sub['payoff_mean'].mean()   if not sub.empty else np.nan

        # Dictator
        for temp in [0, 1]:
            sub = dictator_agg[
                (dictator_agg['model'] == model) &
                (dictator_agg['temperature'] == temp)
            ]
            row[f'dictator_T{temp}_shared'] = sub['mean_shared'].mean() if not sub.empty else np.nan

        # Beauty contest
        for temp in [0, 1]:
            sub = beauty_overall[
                (beauty_overall['model'] == model) &
                (beauty_overall['temperature'] == temp)
            ]
            row[f'beauty_T{temp}_number'] = sub['mean_number'].mean() if not sub.empty else np.nan
            row[f'beauty_T{temp}_levelk'] = sub['level_k'].mode()[0]  if not sub.empty else np.nan

        rows.append(row)

    return pd.DataFrame(rows)


# ── Plotting helpers ──────────────────────────────────────────────────────────

def _savefig(name):
    path = os.path.join(RESULTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f'  Saved {path}')


def _hline(ax, y, label, color, ls='--', lw=1.2):
    ax.axhline(y, color=color, linestyle=ls, linewidth=lw, label=label, zorder=0)


def _model_xticks(ax, models):
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels([SHORT_NAME.get(m, m) for m in models], fontsize=7)


# ── Plot 1: Cooperation rate per model per game ───────────────────────────────

def plot_coop_per_game(iter_agg):
    if iter_agg.empty:
        return

    games = ['prisoners_dilemma', 'chicken_game', 'stag_hunt']
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    fig.suptitle('Cooperation Rate per Model per Game\n(all opponents & framings)', fontsize=13)

    for ax, game in zip(axes, games):
        sub   = iter_agg[iter_agg['game'] == game]
        means = sub.groupby('model')['coop_rate'].mean().reindex(MODEL_ORDER)
        stds  = sub.groupby('model')['coop_rate'].std().reindex(MODEL_ORDER).fillna(0)

        ax.bar(range(len(MODEL_ORDER)), means,
               yerr=stds, capsize=4,
               color=[MODEL_COLORS.get(m, 'grey') for m in MODEL_ORDER],
               alpha=0.85, edgecolor='white')

        _model_xticks(ax, MODEL_ORDER)
        ax.set_title(GAME_LABEL[game], fontsize=10)
        ax.set_ylabel('Cooperation Rate')
        ax.set_ylim(0, 1.25)

        if game == 'prisoners_dilemma':
            _hline(ax, 0, 'Nash = D (0)', 'red')
        elif game == 'chicken_game':
            _hline(ax, 0.5, 'Nash mixed (≈0.5)', 'red')
        else:  # stag_hunt
            _hline(ax, 1, 'Nash (C,C)', 'red')
            _hline(ax, 0, 'Nash (D,D)', 'red', ls=':')

        _hline(ax, HUMAN_COOP[game],
               f'Human avg ({HUMAN_COOP[game]:.0%})', 'green')
        ax.legend(fontsize=7, loc='upper right')

    plt.tight_layout()
    _savefig('plot1_coop_per_game.png')


# ── Plot 2: Cooperation T=0 vs T=1 per model per game ────────────────────────

def plot_coop_temp(iter_agg):
    if iter_agg.empty:
        return

    games = ['prisoners_dilemma', 'chicken_game', 'stag_hunt']
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    fig.suptitle('Cooperation Rate: T=0 vs T=1 per Model per Game', fontsize=13)

    x = np.arange(len(MODEL_ORDER))
    width = 0.35

    for ax, game in zip(axes, games):
        sub = iter_agg[iter_agg['game'] == game]
        for temp, offset, hatch, label in [
            (0, -width / 2, '',    'T=0'),
            (1,  width / 2, '///', 'T=1'),
        ]:
            t_sub = sub[sub['temperature'] == temp]
            means = t_sub.groupby('model')['coop_rate'].mean().reindex(MODEL_ORDER).fillna(0)
            stds  = t_sub.groupby('model')['coop_rate'].std().reindex(MODEL_ORDER).fillna(0)
            ax.bar(x + offset, means, width,
                   yerr=stds, capsize=3,
                   label=label, hatch=hatch,
                   alpha=0.82, edgecolor='grey')

        _model_xticks(ax, MODEL_ORDER)
        ax.set_title(GAME_LABEL[game], fontsize=10)
        ax.set_ylabel('Cooperation Rate')
        ax.set_ylim(0, 1.25)
        ax.legend(fontsize=8)

        _hline(ax, HUMAN_COOP[game],
               f'Human avg ({HUMAN_COOP[game]:.0%})', 'green')
        if game == 'prisoners_dilemma':
            _hline(ax, 0, 'Nash = D', 'red')
        elif game == 'chicken_game':
            _hline(ax, 0.5, 'Nash mixed', 'red')

    plt.tight_layout()
    _savefig('plot2_coop_temperature.png')


# ── Plot 3: Beauty Contest line plot ──────────────────────────────────────────

def plot_beauty_rounds(by_round):
    if by_round.empty:
        return

    temps = sorted(by_round['temperature'].unique())
    fig, axes = plt.subplots(1, len(temps), figsize=(7 * len(temps), 5), sharey=True)
    if len(temps) == 1:
        axes = [axes]

    fig.suptitle('Beauty Contest – Mean Chosen Number per Round', fontsize=13)

    for ax, temp in zip(axes, temps):
        sub = by_round[by_round['temperature'] == temp]
        for model in MODEL_ORDER:
            m_sub = sub[sub['model'] == model]
            if m_sub.empty:
                continue
            # average over framings for the line
            agg = m_sub.groupby('round')['mean_number'].mean()
            ax.plot(agg.index, agg.values,
                    label=SHORT_NAME.get(model, model),
                    color=MODEL_COLORS.get(model, 'grey'),
                    marker='o', markersize=3, linewidth=1.8)

        _hline(ax, 50,   'Level 0 (50)',               'grey',   ':')
        _hline(ax, 33,   'Level 1 (33)',               'orange', ':')
        _hline(ax, 22,   'Level 2 (22)',               'purple', ':')
        _hline(ax, 0,    'Nash (0)',                   'red',    '--')
        _hline(ax, HUMAN_BEAUTY_R1,
               f'Human R1 ({HUMAN_BEAUTY_R1})', 'green', '--')

        ax.set_title(f'T={temp}', fontsize=11)
        ax.set_xlabel('Round')
        ax.set_ylabel('Mean Number')
        ax.set_ylim(-5, 65)
        ax.legend(fontsize=7, loc='upper right', ncol=2)

    plt.tight_layout()
    _savefig('plot3_beauty_contest.png')


# ── Plot 4: Dictator Game barplot ─────────────────────────────────────────────

def plot_dictator(dictator_agg):
    if dictator_agg.empty:
        return

    temps = sorted(dictator_agg['temperature'].unique())
    fig, axes = plt.subplots(1, len(temps), figsize=(7 * len(temps), 5), sharey=True)
    if len(temps) == 1:
        axes = [axes]

    fig.suptitle('Dictator Game – Mean Amount Shared per Model', fontsize=13)

    for ax, temp in zip(axes, temps):
        sub   = dictator_agg[dictator_agg['temperature'] == temp]
        means = sub.groupby('model')['mean_shared'].mean().reindex(MODEL_ORDER)
        stds  = sub.groupby('model')['std_shared'].mean().reindex(MODEL_ORDER).fillna(0)

        ax.bar(range(len(MODEL_ORDER)), means,
               yerr=stds, capsize=4,
               color=[MODEL_COLORS.get(m, 'grey') for m in MODEL_ORDER],
               alpha=0.85, edgecolor='white')

        _model_xticks(ax, MODEL_ORDER)
        ax.set_title(f'T={temp}', fontsize=11)
        ax.set_ylabel('Amount Shared (out of 100)')
        ax.set_ylim(0, 130)

        _hline(ax, 0,                    'Nash (0)',                    'red')
        _hline(ax, HUMAN_DICTATOR_SHARE, f'Human avg ({HUMAN_DICTATOR_SHARE}€)', 'green')
        ax.legend(fontsize=8)

    plt.tight_layout()
    _savefig('plot4_dictator_game.png')


# ── Plot 5: Framing effect ────────────────────────────────────────────────────

def plot_framing_effect(pivot_framing):
    if pivot_framing.empty or 'framing_effect' not in pivot_framing.columns:
        return

    games = ['prisoners_dilemma', 'chicken_game', 'stag_hunt']
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    fig.suptitle('Framing Effect – Δ Cooperation Rate (neutral − competitive)', fontsize=13)

    for ax, game in zip(axes, games):
        sub   = pivot_framing[pivot_framing['game'] == game]
        means = sub.groupby('model')['framing_effect'].mean().reindex(MODEL_ORDER)

        colors = ['#2ca02c' if v >= 0 else '#d62728'
                  for v in means.fillna(0)]
        ax.bar(range(len(MODEL_ORDER)), means,
               color=colors, alpha=0.78, edgecolor='white')
        ax.axhline(0, color='black', linewidth=0.9)
        _model_xticks(ax, MODEL_ORDER)
        ax.set_title(GAME_LABEL[game], fontsize=10)
        ax.set_ylabel('Δ Cooperation Rate')

    plt.tight_layout()
    _savefig('plot5_framing_effect.png')


# ── Plot 6: LLM vs LLM heatmaps ──────────────────────────────────────────────

def plot_llmvsllm_heatmaps(llm_agg):
    if llm_agg.empty:
        return

    games = ['prisoners_dilemma', 'chicken_game', 'stag_hunt']
    temps = sorted(llm_agg['temperature'].unique())

    n_rows, n_cols = len(temps), len(games)
    fig, axes = plt.subplots(n_rows, n_cols,
                             figsize=(5.5 * n_cols, 5 * n_rows))
    # normalise axes to 2-D array
    if n_rows == 1 and n_cols == 1:
        axes = [[axes]]
    elif n_rows == 1:
        axes = [list(axes)]
    elif n_cols == 1:
        axes = [[ax] for ax in axes]

    fig.suptitle('LLM vs LLM – Cooperation Rate Heatmap', fontsize=14)

    short = [SHORT_NAME.get(m, m).replace('\n', ' ') for m in MODEL_ORDER]

    for ti, temp in enumerate(temps):
        for gi, game in enumerate(games):
            ax  = axes[ti][gi]
            sub = llm_agg[
                (llm_agg['game'] == game) &
                (llm_agg['temperature'] == temp)
            ]

            matrix = pd.DataFrame(np.nan,
                                  index=MODEL_ORDER, columns=MODEL_ORDER)
            for _, row in sub.iterrows():
                if row['model'] in MODEL_ORDER and row['opponent_model'] in MODEL_ORDER:
                    matrix.loc[row['model'], row['opponent_model']] = row['coop_rate']

            sns.heatmap(
                matrix.astype(float),
                ax=ax,
                vmin=0, vmax=1,
                cmap='RdYlGn',
                annot=True, fmt='.2f',
                xticklabels=short,
                yticklabels=short,
                linewidths=0.5,
                cbar_kws={'shrink': 0.85},
            )
            ax.set_title(f'{GAME_LABEL[game]} | T={temp}', fontsize=9)
            ax.set_xlabel('Opponent model', fontsize=8)
            ax.set_ylabel('Model',          fontsize=8)
            ax.tick_params(axis='x', labelsize=7, rotation=30)
            ax.tick_params(axis='y', labelsize=7, rotation=0)

    plt.tight_layout()
    _savefig('plot6_llmvsllm_heatmaps.png')


# ── Terminal summary ──────────────────────────────────────────────────────────

def print_iterative_summary(iter_agg):
    if iter_agg.empty:
        return
    print('\n  Cooperation rate (mean over opponents & framings):')
    tbl = (
        iter_agg
        .groupby(['model', 'game', 'temperature'])['coop_rate']
        .mean()
        .unstack(['game', 'temperature'])
        .reindex(MODEL_ORDER)
    )
    print(tbl.round(3).to_string())

    print('\n  Nash deviation rate (mean over opponents & framings):')
    tbl2 = (
        iter_agg
        .groupby(['model', 'game', 'temperature'])['nash_dev_rate']
        .mean()
        .unstack(['game', 'temperature'])
        .reindex(MODEL_ORDER)
    )
    print(tbl2.round(3).to_string())

    print('\n  Mean payoff per round (mean over opponents & framings):')
    tbl3 = (
        iter_agg
        .groupby(['model', 'game', 'temperature'])['payoff_mean']
        .mean()
        .unstack(['game', 'temperature'])
        .reindex(MODEL_ORDER)
    )
    print(tbl3.round(2).to_string())


def print_dictator_summary(dictator_agg):
    if dictator_agg.empty:
        return
    print('\n  Mean amount shared (Nash=0, Human≈28):')
    print(dictator_agg.to_string(index=False))


def print_beauty_summary(beauty_overall):
    if beauty_overall.empty:
        return
    print('\n  Beauty contest – mean number & estimated level-k:')
    print(beauty_overall.sort_values(['temperature', 'model']).to_string(index=False))


def print_llmvsllm_summary(llm_agg):
    if llm_agg.empty:
        return
    print('\n  LLM-vs-LLM cooperation rate (mean per row-model, all opponents):')
    tbl = (
        llm_agg
        .groupby(['model', 'game', 'temperature'])['coop_rate']
        .mean()
        .unstack(['game', 'temperature'])
        .reindex(MODEL_ORDER)
    )
    print(tbl.round(3).to_string())


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    sep = '=' * 62
    print(sep)
    print('LLM Game-Theory Experiment – Analysis')
    print(sep)

    print('\nLoading CSV files from results/ ...')
    iter_df, llm_df, dictator_df, beauty_df = load_data()
    print(f'  Iterative rows : {len(iter_df)}')
    print(f'  LLM-vs-LLM rows: {len(llm_df)}')
    print(f'  Dictator rows  : {len(dictator_df)}')
    print(f'  Beauty rows    : {len(beauty_df)}')

    # ── Analyses
    print('\n[1] Iterative games ...')
    iter_agg, pivot_framing = analyze_iterative(iter_df)
    print_iterative_summary(iter_agg)

    print('\n[2] Dictator game ...')
    dictator_agg = analyze_dictator(dictator_df)
    print_dictator_summary(dictator_agg)

    print('\n[3] Beauty contest ...')
    by_round, beauty_overall = analyze_beauty(beauty_df)
    print_beauty_summary(beauty_overall)

    print('\n[4] LLM vs LLM ...')
    llm_agg = analyze_llmvsllm(llm_df)
    print_llmvsllm_summary(llm_agg)

    # ── Summary table
    print('\n[5] Building summary table ...')
    summary = build_summary_table(iter_agg, dictator_agg, beauty_overall, llm_agg)
    summary_path = os.path.join(RESULTS_DIR, 'summary_table.csv')
    summary.to_csv(summary_path, index=False, float_format='%.4f')
    print(f'  Saved {summary_path}')

    # ── Plots
    print('\n[6] Generating plots ...')
    plot_coop_per_game(iter_agg)
    plot_coop_temp(iter_agg)
    plot_beauty_rounds(by_round)
    plot_dictator(dictator_agg)
    plot_framing_effect(pivot_framing)
    plot_llmvsllm_heatmaps(llm_agg)

    print(f'\n{sep}')
    print('Done. All outputs are in results/')
    print(sep)


if __name__ == '__main__':
    main()
