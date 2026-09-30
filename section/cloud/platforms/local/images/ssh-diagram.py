import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(figsize=(9, 4))
ax.set_axis_off()

# Windows box
win = mpatches.FancyBboxPatch((0.05, 0.2), 0.4, 0.6,
                              boxstyle="round,pad=0.02",
                              linewidth=2, edgecolor="#1E90FF",
                              facecolor="#E6F2FF")
ax.add_patch(win)
ax.text(0.25, 0.75, "Windows (Host OS)", ha='center', va='center', fontsize=12, weight='bold')
ax.text(0.25, 0.6, "C:\\Users\\<you>\\.ssh", ha='center', fontsize=10)
ax.text(0.25, 0.5, "- id_rsa\n- id_rsa.pub\n- config", ha='center', fontsize=9)

# WSL2 box
wsl = mpatches.FancyBboxPatch((0.55, 0.2), 0.4, 0.6,
                              boxstyle="round,pad=0.02",
                              linewidth=2, edgecolor="#32CD32",
                              facecolor="#E8F5E9")
ax.add_patch(wsl)
ax.text(0.75, 0.75, "WSL2 (Ubuntu)", ha='center', va='center', fontsize=12, weight='bold')
ax.text(0.75, 0.6, "/home/<you>/.ssh", ha='center', fontsize=10)
ax.text(0.75, 0.5, "- id_rsa (copy or symlink)\n- id_rsa.pub\n- config", ha='center', fontsize=9)

# Arrow showing the mount point
ax.annotate("", xy=(0.5, 0.5), xytext=(0.55, 0.5),
            arrowprops=dict(arrowstyle="<->", linewidth=1.5, color="gray"))
ax.text(0.525, 0.52, "/mnt/c/Users/<you>/.ssh", ha='center', fontsize=8, color="gray")

plt.tight_layout()
plt.savefig("ssh_keys_windows_wsl2.png", dpi=200, transparent=True)
plt.show()