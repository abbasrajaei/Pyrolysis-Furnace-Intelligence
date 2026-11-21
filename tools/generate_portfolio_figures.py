"""Rebuild figures exclusively from the installed public teaching model."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pyrolysis_furnace_intelligence.scenario_engine import run_scenario
from pyrolysis_furnace_intelligence.fuels import fuel_properties,fuel_required
from pyrolysis_furnace_intelligence.cases import parameter
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'assets'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#173443','text.color':'#173443','axes.titleweight':'bold','figure.facecolor':'#f5f8fa','axes.facecolor':'#f5f8fa'})
COLORS=['#21758a','#d58037','#8eabb8'];evidence={}
def save(fig,name,caption):
    fig.text(.06,.035,caption,fontsize=10,color='#425b68');fig.savefig(ASSETS/(name+'.png'),dpi=160,bbox_inches='tight');plt.close(fig)
normal=run_scenario();changed=run_scenario('zone_redistribution')
fig,ax=plt.subplots(figsize=(10,4.6));fig.subplots_adjust(bottom=.2)
values=[parameter('thermal','radiant').value/1e6,parameter('thermal','convection').value/1e6,normal['heat_balance']['loss']['value']/1e6]
left=0
for value,label,color in zip(values,['Radiant','Convection','Unallocated residual'],COLORS):
    ax.barh(['Chemical input'],[value],left=left,color=color,height=.4,label=label)
    ax.text(left+value/2,0,f'{value:g} MW',ha='center',va='center',color='white',weight='bold');left+=value
ax.set_ylim(-.3,.4);ax.set_xlim(0,60);ax.set_xlabel('Duty / MW');ax.set_title('60 MW input: static heat accounting',loc='left',pad=20);ax.legend(loc='upper center',ncol=3,frameon=False)
save(fig,'heat_balance','SYNTHETIC TEACHING CASE • Residual is not an identified wall or stack loss.')
evidence['heat_balance']={'input_MW':60,'radiant_MW':values[0],'convection_MW':values[1],'residual_MW':values[2]}
fuels=['baseline','high_mass_lhv','lower_mass_lhv'];labels=['Baseline','High mass LHV','Lower mass LHV'];q=parameter('thermal','fired');props=[fuel_properties(k) for k in fuels]
masses=[fuel_required(q,p['lhv']).value for p in props];lhvs=[p['lhv'].value/1e6 for p in props]
fig,axs=plt.subplots(1,2,figsize=(11,4.8));fig.subplots_adjust(bottom=.24,wspace=.3)
for ax,vals,title,unit in zip(axs,[lhvs,masses],['Declared fuel mass heating value','Equivalent fuel at 60 MW'],['LHV / MJ kg⁻¹','Fuel / kg s⁻¹']):
    bars=ax.bar(labels,vals,color=COLORS,width=.6);ax.set_title(title,loc='left',pad=18);ax.set_ylabel(unit);ax.set_ylim(0,max(vals)*1.22)
    ax.bar_label(bars,fmt='%.3g',padding=5)
save(fig,'fuel_comparison','SYNTHETIC MIXTURES + ROUNDED REFERENCES • Fixed chemical duty; no predicted heat-transfer or COT response.')
evidence['fuel_comparison']={'fuels':fuels,'lhv_MJ_kg':lhvs,'equivalent_mass_kg_s':masses}
fig,ax=plt.subplots(figsize=(10,4.8));fig.subplots_adjust(bottom=.23);x=list(range(6))
before=normal['allocation']['value']['zones'];after=changed['allocation']['value']['zones']
ax.bar([i-.19 for i in x],[v/1e6 for v in before],.36,color=COLORS[2],label='Balanced');ax.bar([i+.19 for i in x],[v/1e6 for v in after],.36,color=COLORS[0],label='Explicit Zone C teaching correction')
ax.set_xticks(x,list('ABCDEF'));ax.set_ylabel('Inlet zone duty / MW');ax.set_title('Redistribution changes location, not total inlet duty',loc='left',pad=20);ax.legend(frameon=False,loc='upper left');ax.set_ylim(0,9)
save(fig,'zone_redistribution',f'SYNTHETIC TEACHING CASE • Inlet total: {sum(before)/1e6:g} MW before and after • No temperature-to-firing gain.')
evidence['zone_redistribution']={'before_W':before,'after_W':after,'inlet_total_W':sum(before)}
def box(ax,x,y,w,h,title,body,color='#21758a'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.015',facecolor='white',edgecolor=color,linewidth=1.6))
    ax.text(x+w/2,y+h*.72,title,ha='center',va='center',weight='bold',fontsize=12)
    ax.text(x+w/2,y+h*.35,body,ha='center',va='center',fontsize=11)
def arrow(ax,a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#21758a','lw':1.8})
fig,ax=plt.subplots(figsize=(11,4.8));fig.subplots_adjust(bottom=.2);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');ax.set_title('A pressure constraint changes functional authority',loc='left',pad=20)
box(ax,.04,.35,.36,.4,'Normal teaching state',normal['active_authority']);pressure=run_scenario('pressure_override');box(ax,.59,.35,.36,.4,'Pressure-constraint event',pressure['active_authority']);arrow(ax,(.42,.55),(.57,.55));ax.text(.5,.17,'Reference flows retained • No pressure threshold or valve position inferred',ha='center')
save(fig,'control_authority_example','SYNTHETIC TEACHING EVENT • Authority is not measured physical response or a safety determination.')
evidence['control_authority_example']={'normal_authority':normal['active_authority'],'constraint_authority':pressure['active_authority']}
fig,ax=plt.subplots(figsize=(11,6));fig.subplots_adjust(bottom=.15);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');ax.set_title('Bounded explanations follow verified engineering state',loc='left',pad=20)
box(ax,.03,.71,.25,.2,'Teaching event','Static scenario');box(ax,.375,.71,.25,.2,'Verified state','Current public evidence');box(ax,.72,.71,.25,.2,'Interpretation','Deterministic baseline')
arrow(ax,(.29,.81),(.36,.81));arrow(ax,(.64,.81),(.70,.81))
box(ax,.03,.36,.25,.2,'Grounding pack','Optional provider');box(ax,.375,.36,.25,.2,'Assessment','Exact validator');box(ax,.72,.36,.25,.2,'Accepted result','Bounded catalogue')
arrow(ax,(.5,.70),(.155,.58));arrow(ax,(.29,.46),(.36,.46));arrow(ax,(.64,.46),(.70,.46))
box(ax,.375,.035,.25,.18,'Fallback','No provider / rejection');arrow(ax,(.5,.345),(.5,.235))
save(fig,'scenario_reasoning','PUBLIC TEACHING ARCHITECTURE • Optional AI cannot change engine authority • Demo provider is deterministic.')
evidence['scenario_reasoning']={'basis':'Public grounding and validator architecture; no model-performance data'}
(ASSETS/'figure_data.json').write_text(json.dumps(evidence,indent=2)+'\n')
