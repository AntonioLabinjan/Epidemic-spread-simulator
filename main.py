import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import random

## CHANGABLE; CHATGPT DAJE RAZNE COMBOS
NUM_AGENTS = 500                  # dovoljno ljudi da se vide efekti, ali da nije previše sporo
INIT_INFECTED = 10               # počinje s manjom bazom zaraženih da krene "eksplozija"
INFECTION_RADIUS_BASE = 0.07     # umjereni radius zaraze - nije preširok da se ne razmaše odmah
INFECTION_PROB_BASE = 0.15       # solidna šansa da se zarazi netko u blizini
RECOVERY_TIME = 100              # dovoljno dugo da se vidi razdoblje širenja i pada
DEATH_PROB = 0.07                # realna umjerena smrtnost - izaziva strah i dinamiku
NEW_INFECTION_EVERY = 20         # povremena “nova infekcija iz okoline” da se sustav ne smiri prerano

# Karantena settings
QUARANTINE_PROB = 0.4            # dosta ljudi ide u karantenu, pa se vidi koliko to usporava širenje
QUARANTINE_POS = np.array([0.5, 0.5])
QUARANTINE_RADIUS = 0.1
QUARANTINE_SPEED_FACTOR = 0.02   # karantena je spora, ali ne mrtva, ipak se kreću ka “sigurnom mjestu”


# Agent states
SUSCEPTIBLE, INFECTED, RECOVERED, DEAD, QUARANTINED = 0, 1, 2, 3, 4
STATE_COLORS = {
    SUSCEPTIBLE: 'blue',
    INFECTED: 'red',
    RECOVERED: 'green',
    DEAD: 'black',
    QUARANTINED: 'orange'
}

class Agent:
    def __init__(self):
        self.pos = np.random.rand(2)
        self.vel = (np.random.rand(2) - 0.5) * 0.02
        self.state = SUSCEPTIBLE
        self.infection_timer = 0
        self.is_super_spreader = False
        self.speed_factor = 1.0  # umor smanjuje speed, počinje na 1

    def move(self):
        if self.state == DEAD:
            return
        if self.state == QUARANTINED:
            # Agent se sporo kreće prema karanteni unutar radijusa
            direction = QUARANTINE_POS - self.pos
            dist = np.linalg.norm(direction)
            if dist > QUARANTINE_RADIUS:
                direction = direction / dist  # unit vector
                self.pos += direction * 0.005  # sporo prema karanteni
            # dodaj mali šum za realističnost
            self.pos += (np.random.rand(2) - 0.5) * 0.001
            return
        
        # normalno kretanje s umorom
        self.pos += self.vel * self.speed_factor
        # odbijanje od zidova
        for i in [0, 1]:
            if self.pos[i] < 0 or self.pos[i] > 1:
                self.vel[i] *= -1
        # dodaj šum u poziciju
        self.pos += (np.random.rand(2) - 0.5) * 0.001
        self.pos = np.clip(self.pos, 0, 1)

    def infect(self):
        if self.state == SUSCEPTIBLE:
            self.state = INFECTED
            self.infection_timer = RECOVERY_TIME
            # 10% šansa da je super širitelj (širi virus dalje i jače)
            self.is_super_spreader = (random.random() < 0.1)

    def update(self):
        
        if self.state == DEAD:
            return

        if self.state == INFECTED:
            # s vremenom infekcije, umor raste pa se kreće sporije
            self.speed_factor = max(0.1, 1 - (RECOVERY_TIME - self.infection_timer) / RECOVERY_TIME)
            self.move()  # **dodaj ovo! agent se kreće i kad je zaražen**
            self.infection_timer -= 1
            
            # 30% šanse da se povuče u karantenu na početku infekcije
            if self.infection_timer == RECOVERY_TIME - 5 and random.random() < QUARANTINE_PROB:
                self.state = QUARANTINED
            
            if self.infection_timer <= 0:
                if np.random.rand() < DEATH_PROB:
                    self.state = DEAD
                else:
                    self.state = RECOVERED
                self.speed_factor = 1.0  # reset

        elif self.state == QUARANTINED:
            # Karantena traje do kraja infekcije
            # kreće se sporo prema karanteni u move() pozivu (zapravo u update logici si to uredno odradio)
            self.infection_timer -= 1
            if self.infection_timer <= 0:
                if np.random.rand() < DEATH_PROB:
                    self.state = DEAD
                else:
                    self.state = RECOVERED
                self.speed_factor = 1.0  # reset

            # Karantena ima poseban move kod kojeg se polako giba prema karanteni,
            # jer je u move() logici definirano za QUARANTINED state

            self.move()

        else:
            # zdrav (susceptible ili recovered) ide normalno
            self.speed_factor = 1.0
            self.move()



agents = [Agent() for _ in range(NUM_AGENTS)]
for i in range(min(INIT_INFECTED, NUM_AGENTS)):
    agents[i].infect()

history_S, history_I, history_R, history_D, history_Q = [], [], [], [], []

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
sc = ax1.scatter([], [], s=10)
line_S, = ax2.plot([], [], color="blue")
line_I, = ax2.plot([], [], color="red")
line_R, = ax2.plot([], [], color="green")
line_D, = ax2.plot([], [], color="black")
line_Q, = ax2.plot([], [], color="orange")

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
    "Q": ax2.text(0.75, 0.75, "", transform=ax2.transAxes, color="orange"),
}

MAX_AGENTS = 500  # ili koliko hoćeš maksimalno, ili None za bez ograničenja
NEW_INFECTED_EVERY = 50  # svakih 50 frameova dodaj novog INFECTED agenta

def animate(frame):
    positions = []
    colors = []

    # 1. Update all agents
    for agent in agents:
        agent.update()
        positions.append(agent.pos)
        colors.append(STATE_COLORS[agent.state])

    # 2. Infection logic (isto kao i prije)
    newly_infected = []
    for agent in agents:
        if agent.state in [INFECTED, QUARANTINED]:
            radius = INFECTION_RADIUS_BASE * (3 if agent.is_super_spreader else 1)
            base_prob = INFECTION_PROB_BASE * (1.5 if agent.is_super_spreader else 1)
            intensity_factor = agent.infection_timer / RECOVERY_TIME
            effective_prob = base_prob * intensity_factor
            
            for other in agents:
                if other.state == SUSCEPTIBLE:
                    dist = np.linalg.norm(agent.pos - other.pos)
                    if dist < radius and np.random.rand() < effective_prob:
                        newly_infected.append(other)
    for agent in newly_infected:
        agent.infect()

    # 3. Nova infekcija iz okoline (postojeći kod)
    if frame % NEW_INFECTION_EVERY == 0:
        candidates = [a for a in agents if a.state == SUSCEPTIBLE]
        if candidates:
            random.choice(candidates).infect()

    # 4. Dodaj novog infected agenta svakih NEW_INFECTED_EVERY frameova
    if frame % NEW_INFECTED_EVERY == 0:
        if MAX_AGENTS is None or len(agents) < MAX_AGENTS:
            new_agent = Agent()
            new_agent.state = INFECTED
            new_agent.infection_timer = RECOVERY_TIME
            new_agent.is_super_spreader = (random.random() < 0.1)
            # Stavi ga na random poziciju, random brzinu, odmah može širiti
            new_agent.pos = np.random.rand(2)
            new_agent.vel = (np.random.rand(2) - 0.5) * 0.02
            agents.append(new_agent)

    # 5. Broji stanja
    counts = [0, 0, 0, 0, 0]
    for a in agents:
        counts[a.state] += 1

    history_S.append(counts[SUSCEPTIBLE])
    history_I.append(counts[INFECTED])
    history_R.append(counts[RECOVERED])
    history_D.append(counts[DEAD])
    history_Q.append(counts[QUARANTINED])

    # 6. Update vizualizacije
    sc.set_offsets(np.array(positions))
    sc.set_color(colors)
    ax1.set_title(
        f"Frame {frame} | S: {counts[SUSCEPTIBLE]}  I: {counts[INFECTED]}  R: {counts[RECOVERED]}  D: {counts[DEAD]}  Q: {counts[QUARANTINED]}  Total: {len(agents)}"
    )

    x_vals = np.arange(len(history_S))
    line_S.set_data(x_vals, history_S)
    line_I.set_data(x_vals, history_I)
    line_R.set_data(x_vals, history_R)
    line_D.set_data(x_vals, history_D)
    line_Q.set_data(x_vals, history_Q)

    ax2.set_xlim(0, max(100, len(history_S)))

    # Update legende
    state_map = {"S": SUSCEPTIBLE, "I": INFECTED, "R": RECOVERED, "D": DEAD, "Q": QUARANTINED}
    for key, label in legend_labels.items():
        label.set_text(f"{key}: {counts[state_map[key]]}")

    return [sc, line_S, line_I, line_R, line_D, line_Q, *legend_labels.values()]

ani = animation.FuncAnimation(fig, animate, frames=1000, interval=30, blit=True)
plt.tight_layout()
plt.show()

# Export data
with open("epidemic_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Frame", "Susceptible", "Infected", "Recovered", "Dead", "Quarantined"])
    for i in range(len(history_S)):
        writer.writerow([i, history_S[i], history_I[i], history_R[i], history_D[i], history_Q[i]])
