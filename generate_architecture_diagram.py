"""
Generate Architecture Diagram for AishIngAnalyzer
Creates a professional visual representation of the 5-layer system
Run once: python generate_architecture_diagram.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure
fig, ax = plt.subplots(figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# Color scheme
colors = {
    'layer1': '#E8F4F8',  # Light blue
    'layer2': '#FFF4E6',  # Light orange
    'layer3': '#F0F8E8',  # Light green
    'layer4': '#F8E8F4',  # Light purple
    'layer5': '#FFE8E8',  # Light red
    'title': '#2C3E50',
    'text': '#34495E',
    'accent': '#3498DB'
}

# Title
ax.text(8, 11.5, 'AishIngAnalyzer Architecture',
        fontsize=24, fontweight='bold', ha='center', color=colors['title'])
ax.text(8, 11, 'Multi-Agent Cosmetic Ingredient Safety Analysis System',
        fontsize=14, ha='center', color=colors['text'], style='italic')

# Layer 5: Observability (Top)
layer5_box = FancyBboxPatch((0.5, 9.5), 15, 1.2,
                            boxstyle="round,pad=0.1",
                            edgecolor='#E74C3C', linewidth=2,
                            facecolor=colors['layer5'], alpha=0.7)
ax.add_patch(layer5_box)
ax.text(1, 10.5, 'LAYER 5: OBSERVABILITY', fontsize=12, fontweight='bold', color='#C0392B')
ax.text(1, 10.1, '• LangSmith Tracing: Full workflow visibility', fontsize=9, color=colors['text'])
ax.text(5.5, 10.1, '• Metrics: Time, Retries, Tool Usage, Costs', fontsize=9, color=colors['text'])
ax.text(10, 10.1, '• Dashboard: smith.langchain.com', fontsize=9, color=colors['text'])

# Layer 4: Multi-Agent Workflow (LangGraph)
layer4_box = FancyBboxPatch((0.5, 7), 15, 2.2,
                            boxstyle="round,pad=0.1",
                            edgecolor='#9B59B6', linewidth=2,
                            facecolor=colors['layer4'], alpha=0.7)
ax.add_patch(layer4_box)
ax.text(1, 9, 'LAYER 4: MULTI-AGENT WORKFLOW (LangGraph)', fontsize=12, fontweight='bold', color='#8E44AD')

# Agent boxes
agent_y = 8.5
agents = [
    ('Supervisor\nAgent', 1.5, 'Routes workflow\nMax 5 retries'),
    ('Research\nAgent', 4.5, 'Qdrant + Tavily\nData gathering'),
    ('Analysis\nAgent', 7.5, 'Gemini 2.0\nSafety reports'),
    ('Critic\nAgent', 10.5, '5-gate validation\nQuality control')
]

for agent_name, x_pos, description in agents:
    agent_box = FancyBboxPatch((x_pos, agent_y - 0.5), 2, 1,
                               boxstyle="round,pad=0.05",
                               edgecolor='#8E44AD', linewidth=1.5,
                               facecolor='white', alpha=0.9)
    ax.add_patch(agent_box)
    ax.text(x_pos + 1, agent_y + 0.2, agent_name, fontsize=9,
            fontweight='bold', ha='center', va='center', color='#8E44AD')
    ax.text(x_pos + 1, agent_y - 0.2, description, fontsize=7,
            ha='center', va='center', color=colors['text'])

# Arrows between agents
arrow_y = agent_y
for i in range(len(agents) - 1):
    arrow = FancyArrowPatch((agents[i][1] + 2.1, arrow_y),
                           (agents[i+1][1] - 0.1, arrow_y),
                           arrowstyle='->', mutation_scale=20,
                           linewidth=2, color='#8E44AD')
    ax.add_patch(arrow)

# Feedback arrow (Critic -> Supervisor)
feedback_arrow = FancyArrowPatch((12.5, agent_y - 0.6), (1.5, agent_y - 0.6),
                                arrowstyle='->', mutation_scale=15,
                                linewidth=1.5, color='#E74C3C',
                                linestyle='dashed')
ax.add_patch(feedback_arrow)
ax.text(7, 7.6, 'Retry Loop', fontsize=7, ha='center', color='#E74C3C', style='italic')

# Layer 3: AI/LLM Layer
layer3_box = FancyBboxPatch((0.5, 5.2), 7, 1.5,
                            boxstyle="round,pad=0.1",
                            edgecolor='#27AE60', linewidth=2,
                            facecolor=colors['layer3'], alpha=0.7)
ax.add_patch(layer3_box)
ax.text(1, 6.5, 'LAYER 3: AI/LLM', fontsize=11, fontweight='bold', color='#229954')
ax.text(1, 6.1, '• Model: Gemini 2.0 Flash Experimental', fontsize=9, color=colors['text'])
ax.text(1, 5.75, '• Provider: Google AI Studio', fontsize=9, color=colors['text'])
ax.text(1, 5.4, '• Powers: All 4 agents', fontsize=9, color=colors['text'])

# Layer 2: Tools/Data Layer
layer2_box = FancyBboxPatch((8.5, 5.2), 7, 1.5,
                            boxstyle="round,pad=0.1",
                            edgecolor='#E67E22', linewidth=2,
                            facecolor=colors['layer2'], alpha=0.7)
ax.add_patch(layer2_box)
ax.text(9, 6.5, 'LAYER 2: TOOLS & DATA', fontsize=11, fontweight='bold', color='#D35400')
ax.text(9, 6.1, '• Qdrant: 64 ingredients (vector DB)', fontsize=9, color=colors['text'])
ax.text(9, 5.75, '• Tavily: Web search fallback', fontsize=9, color=colors['text'])
ax.text(9, 5.4, '• Safety Scorer + Allergen Matcher', fontsize=9, color=colors['text'])

# Layer 1: Memory/Persistence Layer
layer1_box = FancyBboxPatch((0.5, 3), 15, 1.9,
                            boxstyle="round,pad=0.1",
                            edgecolor='#3498DB', linewidth=2,
                            facecolor=colors['layer1'], alpha=0.7)
ax.add_patch(layer1_box)
ax.text(1, 4.7, 'LAYER 1: MEMORY & PERSISTENCE', fontsize=11, fontweight='bold', color='#2874A6')

# Memory components
memory_items = [
    ('Short-Term\nMemory', 2, 'LangGraph State\nWorkflow context'),
    ('Long-Term\nMemory', 5.5, 'Redis Cloud\nUser profiles'),
    ('Analysis\nHistory', 9, 'Redis Cloud\nPast analyses'),
    ('Session\nManager', 12.5, 'Session tracking\nHistory retrieval')
]

for mem_name, x_pos, description in memory_items:
    mem_box = FancyBboxPatch((x_pos - 0.8, 3.5), 2.2, 1,
                            boxstyle="round,pad=0.05",
                            edgecolor='#2874A6', linewidth=1.5,
                            facecolor='white', alpha=0.9)
    ax.add_patch(mem_box)
    ax.text(x_pos + 0.3, 4.2, mem_name, fontsize=8,
            fontweight='bold', ha='center', va='center', color='#2874A6')
    ax.text(x_pos + 0.3, 3.8, description, fontsize=7,
            ha='center', va='center', color=colors['text'])

# User Interface Layer (Bottom)
ui_box = FancyBboxPatch((0.5, 0.5), 15, 2.2,
                        boxstyle="round,pad=0.1",
                        edgecolor='#16A085', linewidth=2,
                        facecolor='#E8F8F5', alpha=0.7)
ax.add_patch(ui_box)
ax.text(1, 2.5, 'USER INTERFACE: STREAMLIT WEB APP', fontsize=11, fontweight='bold', color='#117A65')

# UI Features
ui_features = [
    ('Profile\nManagement', 2, 'Name, skin type\nallergens, expertise'),
    ('Ingredient\nInput', 5, 'Paste list or\ntype ingredients'),
    ('Live\nAnalysis', 8, 'Real-time progress\nMulti-agent workflow'),
    ('Export\nOptions', 11, 'TXT, PDF, CSV\nDownload reports'),
    ('Observability\nMetrics', 14, 'Performance stats\nData sources')
]

for ui_name, x_pos, description in ui_features:
    ui_item_box = FancyBboxPatch((x_pos - 0.7, 1), 1.8, 0.9,
                                 boxstyle="round,pad=0.05",
                                 edgecolor='#16A085', linewidth=1,
                                 facecolor='white', alpha=0.9)
    ax.add_patch(ui_item_box)
    ax.text(x_pos + 0.2, 1.6, ui_name, fontsize=8,
            fontweight='bold', ha='center', va='center', color='#117A65')
    ax.text(x_pos + 0.2, 1.2, description, fontsize=6,
            ha='center', va='center', color=colors['text'])

# Data Flow Arrows (Vertical connections)
# UI -> Memory
flow1 = FancyArrowPatch((8, 2.7), (8, 3.4),
                       arrowstyle='->', mutation_scale=15,
                       linewidth=2, color='#2C3E50', alpha=0.6)
ax.add_patch(flow1)

# Memory -> Workflow
flow2 = FancyArrowPatch((8, 4.9), (8, 6.9),
                       arrowstyle='->', mutation_scale=15,
                       linewidth=2, color='#2C3E50', alpha=0.6)
ax.add_patch(flow2)

# Tools -> Workflow (horizontal)
flow3 = FancyArrowPatch((8.3, 6), (7.6, 7.8),
                       arrowstyle='->', mutation_scale=15,
                       linewidth=1.5, color='#2C3E50', alpha=0.6)
ax.add_patch(flow3)

# AI -> Workflow (horizontal)
flow4 = FancyArrowPatch((7.6, 6), (6.5, 7.8),
                       arrowstyle='->', mutation_scale=15,
                       linewidth=1.5, color='#2C3E50', alpha=0.6)
ax.add_patch(flow4)

# Observability monitoring (dashed)
obs1 = FancyArrowPatch((8, 9.4), (8, 9.2),
                      arrowstyle='-', mutation_scale=15,
                      linewidth=1.5, color='#E74C3C',
                      linestyle='dashed', alpha=0.5)
ax.add_patch(obs1)

# Legend
legend_elements = [
    mlines.Line2D([0], [0], color='#2C3E50', linewidth=2, label='Data Flow'),
    mlines.Line2D([0], [0], color='#E74C3C', linewidth=2, linestyle='dashed', label='Monitoring/Feedback'),
    mpatches.Patch(facecolor='white', edgecolor='black', label='Component')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9, framealpha=0.9)

# Footer
ax.text(8, 0.2, '© 2025 AishIngAnalyzer | Multi-Agent Cosmetic Ingredient Safety Analysis System',
        fontsize=8, ha='center', color=colors['text'], style='italic')

plt.tight_layout()
plt.savefig('architecture_diagram.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Architecture diagram saved: architecture_diagram.png")
print("📁 Location: c:/Users/aisha/OneDrive/Desktop/Work/AishIngAnalyzer/architecture_diagram.png")
plt.close()
