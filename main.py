import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_AGENTS = 200
INIT_INFECTED = 5
INFECTION_RADIUS = 0.03
INFECTION_PROB = 0.2
RECOVERY_TIME = 300

SUSCEPTIBLE, INFECTED, RECOVERED = 0, 1, 2

class Agent:
    def __init__(self):
        self.pos = np.random.rand(2)
        self.vel = (np.random.rand(2) - 0.5) * 0.02
        self.state = SUSCEPTIBLE
        self.infection_timer = 0

    def move(self):
        self.pos += self.vel
        for i in [0, 1]:
            if self.pos[i] < 0 or self.pos[i] > 1:
                self.vel[i] *= -1

    def infect(self):
        self.state = INFECTED
        self.infection_timer = RECOVERY_TIME

    def update(self):
        self.move()
        if self.state == INFECTED:
            self.infection_timer -= 1
            if self.infection_timer <= 0:
                self.state = RECOVERED

agents = [Agent() for _ in range(NUM_AGENTS)]
for i in range(INIT_INFECTED):
    agents[i].infect()

history_S = []
history_I = []
history_R = []

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
sc = ax1.scatter([], [], s=10)
line_S, = ax2.plot([], [], label="Susceptible", color="blue")
line_I, = ax2.plot([], [], label="Infected", color="red")
line_R, = ax2.plot([], [], label="Recovered", color="green")

ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.set_title("Epidemic Spread")

ax2.set_xlim(0, 1000)
ax2.set_ylim(0, NUM_AGENTS)
ax2.set_title("Epidemic Curve")
ax2.legend()

def animate(frame):
    positions = []
    colors = []

    for agent in agents:
        agent.update()
        positions.append(agent.pos)

        if agent.state == INFECTED:
            for other in agents:
                if other.state == SUSCEPTIBLE:
                    if np.linalg.norm(agent.pos - other.pos) < INFECTION_RADIUS:
                        if np.random.rand() < INFECTION_PROB:
                            other.infect()

        if agent.state == SUSCEPTIBLE:
            colors.append('blue')
        elif agent.state == INFECTED:
            colors.append('red')
        else:
            colors.append('green')

    counts = [0, 0, 0]
    for a in agents:
        counts[a.state] += 1

    history_S.append(counts[SUSCEPTIBLE])
    history_I.append(counts[INFECTED])
    history_R.append(counts[RECOVERED])

    pos_array = np.array(positions)
    sc.set_offsets(pos_array)
    sc.set_color(colors)
    ax1.set_title(f"Spread Simulation — Frame {frame}")

    x_vals = np.arange(len(history_S))
    line_S.set_data(x_vals, history_S)
    line_I.set_data(x_vals, history_I)
    line_R.set_data(x_vals, history_R)
    ax2.set_xlim(0, max(100, len(history_S)))

    return sc, line_S, line_I, line_R

ani = animation.FuncAnimation(fig, animate, frames=1000, interval=30, blit=True)
plt.tight_layout()
plt.show()
