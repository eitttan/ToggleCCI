import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle
from matplotlib.ticker import ScalarFormatter
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'

def plot_cumulative_cost(hourly_cumulative_costs, hours):
    plt.figure(figsize=(12, 6))
    for name, costs in hourly_cumulative_costs.items():
        plt.plot(range(hours), costs, label=name)
    plt.title('Cumulative Cost Over Time per Algorithm')
    plt.xlabel('Hour')
    plt.ylabel('Cumulative Cost [USD]')
    plt.legend()
    plt.grid()

def plot_pair_vpn_monthly(pair, algorithm_name=''):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(pair.monthly_vpn_GB_history)
    ax1.set_ylabel('Traffic [GB]', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.plot(pair.cost_vpn_GB_history, color='red')
    ax2.set_ylabel('VPN cost per GB [USD]', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    plt.title(f'VPN tier charging, pair: {pair.name}, algorithm: {algorithm_name}')

def plot_effective_cost_per_GB(hourly_cumulative_costs, hourly_traffic_volumes, hours):
    cumulative_volume = np.cumsum(hourly_traffic_volumes)
    cumulative_volume[cumulative_volume == 0] = np.nan
    linestyles = cycle(['-', '--', '-.', ':'])
    plt.figure(figsize=(6.2, 4.15))
    for algo, cumulative_cost in hourly_cumulative_costs.items():
        effective_cost = np.asarray(cumulative_cost) / cumulative_volume
        sampled_hours = range(0, hours, 2)
        plt.plot(sampled_hours, effective_cost[list(sampled_hours)], linestyle=next(linestyles), label=algo, linewidth=2)
    plt.xlabel('Hours', fontsize=18)
    plt.ylabel('Cost per GB [USD]', fontsize=18)
    plt.ylim(0, 0.3)
    plt.legend(fontsize=14)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.grid()
    plt.tight_layout()
    plt.savefig('eff.png')
    plt.savefig('eff.pdf', format='pdf', bbox_inches='tight', dpi=300)

def plot_cost_breakdown(leasing_costs, traffic_costs, font_size=18):
    algorithms = list(leasing_costs.keys())
    leasing = [leasing_costs[algo] for algo in algorithms]
    traffic = [traffic_costs[algo] for algo in algorithms]
    x_positions = range(len(algorithms))
    plt.figure(figsize=(6, 4))
    ax = plt.gca()
    ax.bar(x_positions, leasing, color='red', label='Leasing')
    ax.bar(x_positions, traffic, bottom=leasing, color='blue', label='Traffic')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(['VPN', 'CCI', 'All', 'Month', 'ToggleCCI'], fontsize=font_size - 2)
    ax.set_xlabel('Algorithms', fontsize=font_size)
    ax.set_ylabel('Total cost [USD]', fontsize=font_size)
    ax.set_ylim([0, 250000])
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((5, 5))
    ax.yaxis.set_major_formatter(formatter)
    ax.ticklabel_format(axis='y', style='scientific')
    ax.tick_params(axis='y', labelsize=font_size)
    ax.yaxis.get_offset_text().set_fontsize(font_size)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('bars.png')
    plt.savefig('bars.pdf', format='pdf', dpi=300)

def plot_traffic_state_cost2(res, hours, hourly_traffic, cci_state_encoded, cumulative_cost, cci_thresh, vpn_thresh, vpn_cost, cci_cost, algorithm_name):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(hours, hourly_traffic, color='blue', label='Traffic [GB]')
    ax1.set_xlabel('Hour')
    ax1.set_ylabel('Traffic [GB]', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.step(hours, cci_state_encoded, where='post', color='red', label='CCI State')
    ax2.set_ylabel('CCI State', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.plot(hours, cumulative_cost, color='green', label='Algorithm Cost')
    ax3.plot(hours, np.cumsum(vpn_cost), color='blue', label='VPN Cost')
    ax3.plot(hours, np.cumsum(cci_cost), color='brown', label='CCI Cost')
    ax3.set_ylabel('Cumulative Cost [USD]', color='green')
    ax3.tick_params(axis='y', labelcolor='green')
    ax4 = ax1.twinx()
    ax4.spines['right'].set_position(('outward', 120))
    ax4.plot(hours, cci_thresh, color='purple', label='CCI threshold')
    ax4.plot(hours, vpn_thresh, color='orange', label='VPN threshold')
    ax4.set_ylabel('Recent Cost [USD]', color='purple')
    ax4.tick_params(axis='y', labelcolor='purple')
    for h, _ in res['cci_activation_points']:
        ax2.plot(h, 1, 'ro')
    for h, _ in res['cci_decide_points']:
        ax2.plot(h, 1, 'go')
    for h, _ in res['cci_renew_points']:
        ax2.plot(h, 2, 'bs')
    handles = []
    labels = []
    for axis in [ax1, ax2, ax3, ax4]:
        axis_handles, axis_labels = axis.get_legend_handles_labels()
        handles.extend(axis_handles)
        labels.extend(axis_labels)
    ax1.legend(handles, labels, loc='upper left')
    plt.title(f'Traffic, CCI State, and Cumulative Cost ({algorithm_name})')
    plt.tight_layout()
    plot_traffic_state_cost2_simple_for_paper(res, hours, hourly_traffic, cci_state_encoded, cumulative_cost, cci_thresh, vpn_thresh, vpn_cost, cci_cost, algorithm_name)

def plot_debug_monthly(res, hours, hourly_traffic, cci_state_encoded, cumulative_cost, vpn_cost, cci_cost, algorithm_name):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(hours, hourly_traffic, color='blue', label='Traffic [GB]')
    ax1.set_xlabel('Hour')
    ax1.set_ylabel('Traffic [GB]', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax2 = ax1.twinx()
    ax2.step(hours, cci_state_encoded, where='post', color='red', label='CCI State')
    ax2.set_ylabel('CCI State', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.plot(hours, cumulative_cost, color='green', label='Algorithm Cost')
    ax3.plot(hours, np.cumsum(vpn_cost), color='blue', label='VPN Cost')
    ax3.plot(hours, np.cumsum(cci_cost), color='brown', label='CCI Cost')
    ax3.set_ylabel('Cumulative Cost [USD]', color='green')
    ax3.tick_params(axis='y', labelcolor='green')
    plt.title(f'Traffic, CCI State, and Cumulative Cost ({algorithm_name})')

def plot_traffic_state_cost2_simple_for_paper(res, hours, hourly_traffic, cci_state_encoded, cumulative_cost, cci_thresh, vpn_thresh, vpn_cost, cci_cost, algorithm_name):
    plt.figure(figsize=(9, 6))
    ax1 = plt.gca()
    fontsize = 24
    linewidth = 4
    ax1.plot(hours, hourly_traffic, color='blue', label='Traffic', linewidth=3)
    ax1.set_xlabel('Hours', fontsize=fontsize, fontweight='bold')
    ax1.set_ylabel('Traffic per Hour [GB]', color='blue', fontsize=fontsize, fontweight='bold')
    ax1.tick_params(axis='x', labelsize=fontsize)
    ax1.tick_params(axis='y', labelcolor='blue', labelsize=fontsize)
    if len(hours) > 4500:
        ax1.set_xlim([hours[3500], hours[4500]])
    ax4 = ax1.twinx()
    ax4.plot(hours, cci_thresh, color='purple', linestyle='--', label='$R_{\\mathrm{CCI}}$', linewidth=linewidth)
    ax4.plot(hours, vpn_thresh, color='orange', linestyle='-.', label='$R_{\\mathrm{VPN}}$', linewidth=linewidth)
    ax4.set_ylabel('Cost [USD]', color='black', fontsize=fontsize, fontweight='bold')
    ax4.tick_params(axis='y', labelcolor='black', labelsize=fontsize)
    ax4.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax4.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    ax4.yaxis.get_offset_text().set_fontsize(fontsize)
    first = True
    for h, _ in res['cci_decide_points']:
        label = 'CCI Request' if first else None
        ax4.plot(h, cci_thresh[h], 'gd', label=label, markersize=12, linewidth=linewidth)
        first = False
    cci_active = np.array(cci_state_encoded) == 2
    start = None
    for i, active in enumerate(cci_active):
        if active and start is None:
            start = hours[i]
        if not active and start is not None:
            ax1.axvspan(start, hours[i], color='green', alpha=0.1)
            start = None
    if start is not None:
        ax1.axvspan(start, hours[-1], color='green', alpha=0.1)
    background_patch = mpatches.Patch(color='green', alpha=0.1, label='CCI ON')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines4, labels4 = ax4.get_legend_handles_labels()
    ax1.legend(lines1 + lines4 + [background_patch], labels1 + labels4 + ['CCI ON'], loc='upper left', bbox_to_anchor=(-0.025, 1.038), fontsize=fontsize, frameon=True, edgecolor='black', handlelength=2)
    plt.tight_layout()
    plt.savefig('scen.png')
    plt.savefig('scen.pdf', format='pdf', dpi=300)
