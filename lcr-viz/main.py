import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import subprocess

LCR_SIM_BIN = "./lcr-sim"

def main():

    for player_count in range(2, 100):
        wins = get_wins(10_000_000, player_count)
        winner_index = max(range(len(wins)), key=wins.__getitem__)
        print(f"{player_count},{winner_index+1}")

    #for i in range(1, 101):
    #    generate_and_save_sim(1000 * i, 30, "output/" + str(i) + ".png")
    #generate_and_save_sim(10000000, 10, "output/10M_10.png")
    #print("100")
    #generate_and_save_sim(10000000, 100, "output/10M_100.png")

def generate_and_save_sim(num_games, num_players, file_name):
    wins = get_wins(num_games, num_players)

    fig, ax = plt.subplots()
    ax.set(ylabel="Wins", xlabel="Player", title=f"Win Counts of {num_players} Players After {num_games} Games")
    ax.bar(range(num_players), wins)
    fig.savefig(file_name)


def get_wins(num_games, num_players, money=5, progress_bar=False):
    if progress_bar:
        data = subprocess.run((LCR_SIM_BIN, "-g", str(num_games), "-p", str(num_players), "-m", str(money), "-s", "--progress"), stdout=subprocess.PIPE)
    else:
        data = subprocess.run((LCR_SIM_BIN, "-g", str(num_games), "-p", str(num_players), "-m", str(money), "-s"), stdout=subprocess.PIPE)
    
    return [int(i) for i in data.stdout.decode("utf-8").split()]

if __name__ == "__main__":
    main()
