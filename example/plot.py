#!/Users/dnjf/micromamba/envs/def/bin/python

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re
import pandas as pd

pots=['ref', 'dft', '7net-0','omni', 'ompa','ompas_wso','ompas']
systems=['225_MgO','186_GaN','186_AlN','186_ZnO','167_CaCO3','14_ZrO2','216_GaAs','227_Si', '62_YAlO3']
wd = '/Users/dnjf/projects/QHA'
eos = 'birch_murnaghan'

def _set_rcParams(plt):
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica','Arial']
    # plt.rcParams['mathtext.fontset'] = 'cm'
    plt.rcParams['font.size'] = 9
    plt.rcParams['axes.labelsize'] = 9
    plt.rcParams['axes.titlesize'] = 9
    plt.rcParams['axes.titlelocation'] = 'right'
    plt.rcParams['axes.titlepad'] = 3

    plt.rcParams['xtick.labelsize'] = 8
    plt.rcParams['ytick.labelsize'] = 8
    plt.rcParams['axes.linewidth'] = 0.7
    plt.rcParams['xtick.labelbottom'] = True    
    plt.rcParams['legend.frameon'] = True
    plt.rcParams['legend.loc'] = 'lower right'
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    plt.rcParams['xtick.major.size'] = 4
    plt.rcParams['xtick.major.width'] = 0.4
    plt.rcParams['xtick.minor.size'] = 2.5
    plt.rcParams['xtick.minor.width'] = 0.3

    plt.rcParams['ytick.major.size'] = 5
    plt.rcParams['ytick.minor.size'] = 4
    plt.rcParams['ytick.major.width'] = 0.4
    plt.rcParams['ytick.minor.width'] = 0.3
    plt.rcParams['legend.fontsize'] = 8
    plt.rcParams['legend.facecolor'] = 'white'

    plt.rcParams['figure.figsize'] = 3.4, 2.5
    plt.rcParams['savefig.dpi'] = 600
    plt.rcParams['lines.linewidth'] = 1
    plt.rcParams['figure.subplot.bottom'] = 0.15
    plt.rcParams['figure.subplot.left'] = 0.15
    plt.rcParams['figure.subplot.right'] = 0.95
    plt.rcParams['figure.subplot.top'] = 0.9
    plt.rcParams['figure.subplot.wspace'] = 0.15
    plt.rcParams['figure.subplot.hspace'] = 0.15

    # plt.rcParams['axes.grid'] = True


def get_title(full_system):
    spg_num, system = full_system.split('_')
    title = full_system
    if spg_num=='225':
        title = system+ r' (Fm$\overline{3}$m)'
    elif spg_num=='216':
        title = system+r' (F$\overline{4}$3m)'
    elif spg_num=='227':
        title = system+r' (Fd$\overline{3}$m)'
    elif spg_num=='186':
        title = fr'{system} (P6$_{3}$mc)'
    elif spg_num=='167':
        title = system+r' (R$\overline{3}$c)'
    elif spg_num=='14':
        title = fr'{system} (P2$_{1}$/c)'
    elif spg_num=='62':
        title = fr'{system} (Pnma)'
    return title

def _tweak_legend(ax):
    # ax.legend(loc='lower right', ncols=2,fontsize=15, frameon=True, handlelength=1.8, handletextpad=0.5, columnspacing=0.7, borderpad=0.6, labelspacing=0.5, markerscale=1,edgecolor='black', facecolor='none', framealpha=1, prop={'weight':'bold'})
    ax.legend(loc='upper left', bbox_to_anchor=(.02, 0.99), ncols=2,fontsize=15, 
              frameon=True, handlelength=1.8, handletextpad=0.5, columnspacing=0.7, 
              borderpad=0.6, labelspacing=0.5, markerscale=1,edgecolor='black', 
              facecolor='none', framealpha=1, prop={'weight':'bold'})
    pass

def _get_title(full_system):
    spg_num, system = full_system.split('_')
    title = full_system
    if spg_num=='225':
        title = system+ r' (Fm$\overline{3}$m)'
    elif spg_num=='216':
        title = system+r' (F$\overline{4}$3m)'
    elif spg_num=='227':
        title = system+r' (Fd$\overline{3}$m)'
    elif spg_num=='186':
        title = fr'{system} (P6$_{3}$mc)'
    elif spg_num=='167':
        title = system+r' (R$\overline{3}$c)'
    elif spg_num=='14':
        title = fr'{system} (P2$_{1}$/c)'
    elif spg_num=='62':
        title = fr'{system} (Pnma)'
    return title

pots=['ref', 'dft','7net-0','ompa','omni','ompas_wso','ompas']

def plot_ctes(system, wd, modal='mpa', mid='.', wo7=False, mixed=False, task='qha'):
    title = get_title(system)
    fig, ax = plt.subplots(layout='compressed')
    ax.axhline(0, color='grey', lw=0.5, ls='--')
    ERROR=0
    for pot in pots:

        df_dir = get_dir(pot, system, wd, task=task, modal=modal, mid=mid)
        if wo7 and pot == '7net-0':
            continue
        if os.path.exists(f'{df_dir}/thermal_expansion.csv') is False and pot != 'ref':
            print(f"File not found: {df_dir}/thermal_expansion.csv")
            ERROR += 1
            continue
        if mixed and pot == '7net-0':
            if mid == 'e5':
                df_dir = get_dir(pot, system, wd, task=task, modal=modal, mid='e10')
            elif mid == 'e10':
                df_dir = get_dir(pot, system, wd, task=task, modal=modal, mid='e5')
            elif mid == 'e5_d3':
                df_dir = get_dir(pot, system, wd, task=task, modal=modal, mid='e10_d3')
            elif mid == 'e10_d3':
                df_dir = get_dir(pot, system, wd, task=task, modal=modal, mid='e5_d3')

        try:
            df = pd.read_csv(f'{df_dir}/thermal_expansion.csv').loc[:500]
            ax.plot(df['temperature'], np.array(df['cte'])*1e5, label=label_dict[pot], color=color_dict[pot], ls=line_dict[pot], alpha = 0.75 if pot in ['ompas_wso','dft'] else 1, zorder=1 if pot in ['ompas_wso','dft'] else 2)
        except Exception as e:
            print(f"Error processing {pot}: {e}")
            # ERROR += 1
            continue

    ax.set_xlabel(r'Temperature ($\mathsf{K}$)')
    ax.set_ylabel(r'$\mathsf{\alpha^{V}} \ (10^{-5}\,\mathsf{K}^{-1})$')
    # ax.set_title( fr'$\mathrm{{system}}$')
    # ax.set_title( r'$\mathrm{GaAs\ (F\overline{4}3m)}$')

    ax.set_title(title)
    # ax.set_xlim(-50,1050) 

    ax.set_xlim(0, 1000)
    # ax.set_ylim(-.2, 4.5)

    # ax.set_xticks(np.arange(0, 1001, 200))
    # ax.set_yticks(np.arange(-0.0, 3.5, 0.5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
 
    legend = ax.legend(ncols=2, columnspacing=0.7, handlelength=1.5, markerscale=1.5, handletextpad=0.5, borderpad=0.3)
    frame = legend.get_frame()
    frame.set_boxstyle('square')
    frame.set_linewidth(1)
    if ERROR > 0:
        print(f"Warning: {ERROR} errors encountered while processing data for {system} with modal {modal} and mid {mid}.")
    else:
        if mixed:
            os.makedirs(f'{wd}/{system}/figures/mixed', exist_ok=True)
            fig_dir = f'{wd}/{system}/figures/mixed/{system}_{modal}_{mid}_{task.split("_")[-1]}_7{int(not wo7)}.png'
            plt.savefig(fig_dir, bbox_inches='tight')
        else:
            os.makedirs(f'{wd}/{system}/figures/7{int(not wo7)}', exist_ok=True)
            fig_dir = f'{wd}/{system}/figures/7{int(not wo7)}/{modal}_{mid}_{task.split("_")[-1]}_7{int(not wo7)}.png'
            plt.savefig(fig_dir, bbox_inches='tight')
        # plt.savefig(f'test2_{system}.png', bbox_inches='tight')
    plt.show()
    # plt.close()

modals = ['omat24', 'mpa']
mids = ['e10', 'e5', 'e10_d3', 'e5_d3']
tasks = ['qha_v', 'qha_m', 'qha_bm']
systems=['225_Al','225_MgO','186_GaN','186_AlN','186_ZnO','167_CaCO3','14_ZrO2','216_GaAs','227_Si', '62_YAlO3']

# for system in systems:
#     for mid in mids:
#         for modal in modals:
#             print(f"Plotting for {system} with modal {modal} and mid {mid}")
#             for task in tasks:
#                 plot_ctes(system, wd, modal=modal, mid=mid, wo7=True, mixed=False, task=task)
#                 plot_ctes(system, wd, modal=modal, mid=mid, wo7=False, mixed=False, task=task)

# plot_ctes('225_Al', wd, modal='mpa', mid='e10', wo7=not True)
# plot_ctes('14_ZrO2', wd, modal='omat24', mid='e5', wo7=True)