import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import random

# Settings

NUM_AGENTS = 200
INIT_INFECTED = 1
INFECTION_RADIUS = 0.03
INFECTION_PROB = 0.2
RECOVERY_TIME = 300
DEATH_PROB = 0.05
NEW_INFECTION_EVERY = 15  # nova infekcija svakih X frameova


assert INIT_INFECTED <= NUM_AGENTS, "Cannot infect more agents than exist!"


# Agent states
SUSCEPTIBLE, INFECTED, RECOVERED, DEAD = 0, 1, 2, 3
STATE_COLORS = {SUSCEPTIBLE: 'blue', INFECTED: 'red', RECOVERED: 'green', DEAD: 'black'}

class Agent:
    def __init__(self):
        self.pos = np.random.rand(2)
        self.vel = (np.random.rand(2) - 0.5) * 0.02
        self.state = SUSCEPTIBLE
        self.infection_timer = 0

    def move(self):
        if self.state == DEAD:
            return
        self.pos += self.vel
        for i in [0, 1]:
            if self.pos[i] < 0 or self.pos[i] > 1:
                self.vel[i] *= -1

    def infect(self):
        if self.state == SUSCEPTIBLE:
            self.state = INFECTED
            self.infection_timer = RECOVERY_TIME

    def update(self):
        if self.state != DEAD:
            self.move()
        if self.state == INFECTED:
            self.infection_timer -= 1
            if self.infection_timer <= 0:
                if np.random.rand() < DEATH_PROB:
                    self.state = DEAD
                else:
                    self.state = RECOVERED

agents = [Agent() for _ in range(NUM_AGENTS)]
for i in range(INIT_INFECTED):
    agents[i].infect()

history_S, history_I, history_R, history_D = [], [], [], []

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
sc = ax1.scatter([], [], s=10)
line_S, = ax2.plot([], [], color="blue")
line_I, = ax2.plot([], [], color="red")
line_R, = ax2.plot([], [], color="green")
line_D, = ax2.plot([], [], color="black")

ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.set_title("Epidemic Spread")

ax2.set_xlim(0, 1000)
ax2.set_ylim(0, NUM_AGENTS)
ax2.set_title("Epidemic Curve")

legend_labels = {
    "S": ax2.text(0.75, 0.95, "", transform=ax2.transAxes, color="blue"),
    "I": ax2.text(0.75, 0.90, "", transform=ax2.transAxes, color="red"),
    "R": ax2.text(0.75, 0.85, "", transform=ax2.transAxes, color="green"),
    "D": ax2.text(0.75, 0.80, "", transform=ax2.transAxes, color="black"),
}

def animate(frame):
    positions = []
    colors = []

    # 1. Update all agents
    for agent in agents:
        agent.update()
        positions.append(agent.pos)
        colors.append(STATE_COLORS[agent.state])

    # 2. Collect new infections (batch infection phase)
    newly_infected = []
    for agent in agents:
        if agent.state == INFECTED:
            for other in agents:
                if other.state == SUSCEPTIBLE:
                    if np.linalg.norm(agent.pos - other.pos) < INFECTION_RADIUS:
                        if np.random.rand() < INFECTION_PROB:
                            newly_infected.append(other)
    for agent in newly_infected:
        agent.infect()

    # 3. Inject new infection every X frames
    if frame % NEW_INFECTION_EVERY == 0:
        candidates = [a for a in agents if a.state == SUSCEPTIBLE]
        if candidates:
            random.choice(candidates).infect()

    # 4. Count states
    counts = [0, 0, 0, 0]
    for a in agents:
        counts[a.state] += 1

    history_S.append(counts[SUSCEPTIBLE])
    history_I.append(counts[INFECTED])
    history_R.append(counts[RECOVERED])
    history_D.append(counts[DEAD])

    # 5. Update scatter and plots
    sc.set_offsets(np.array(positions))
    sc.set_color(colors)
    ax1.set_title(f"Frame {frame} | S: {counts[SUSCEPTIBLE]}  I: {counts[INFECTED]}  R: {counts[RECOVERED]}  D: {counts[DEAD]}")

    x_vals = np.arange(len(history_S))
    line_S.set_data(x_vals, history_S)
    line_I.set_data(x_vals, history_I)
    line_R.set_data(x_vals, history_R)
    line_D.set_data(x_vals, history_D)
    ax2.set_xlim(0, max(100, len(history_S)))

        # Update legend labels (safe!)
    state_map = {"S": SUSCEPTIBLE, "I": INFECTED, "R": RECOVERED, "D": DEAD}
    for key, label in legend_labels.items():
        label.set_text(f"{key}: {counts[state_map[key]]}")


    return [sc, line_S, line_I, line_R, line_D, *legend_labels.values()]

ani = animation.FuncAnimation(fig, animate, frames=1000, interval=30, blit=True)
plt.tight_layout()
plt.show()

# Export data
with open("epidemic_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Frame", "Susceptible", "Infected", "Recovered", "Dead"])
    for i in range(len(history_S)):
        writer.writerow([i, history_S[i], history_I[i], history_R[i], history_D[i]])
