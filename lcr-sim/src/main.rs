use std::sync::Mutex;

use clap::Parser;
use indicatif::{ParallelProgressIterator, ProgressStyle};
use rand::Rng;
use rayon::iter::{IntoParallelIterator, ParallelIterator};

/// Program arguments
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// The number of games to simulate
    #[arg(short, long)]
    games: usize,

    /// The number of players to participate in each game
    #[arg(short, long)]
    players: usize,

    /// The amount of money each player starts with
    #[arg(short, long, default_value_t = 5)]
    money: u32,

    /// Show a progress bar while the simulations are running
    #[arg(long, default_value_t = false)]
    progress: bool,

    /// Only print the results with no extra text
    #[arg(short, long, default_value_t = false)]
    script_mode: bool
}

/// Main!
fn main() {

    let args = Args::parse();

    // Get all the wins - this takes a couple of seconds.
    let wins = simulate_multithreaded(args.players, args.games, args.money, args.progress);

    for i in 0..args.players {
        if args.script_mode {
            println!("{}", wins[i]);
        } else {
            println!("Player {}: {} wins", i, wins[i]);
        }
    }
}

/// Simulates a number of games and tallies the win counts of each player. Uses all available CPU.
fn simulate_multithreaded(num_players: usize, num_games: usize, starting_money: u32, progress_bar: bool) -> Vec<usize> {

    let wins = Mutex::new(vec![0_usize; num_players]);

    if progress_bar {
        // Progress bar setup
        let style = ProgressStyle::with_template("{wide_bar} [{pos}/{len}, {elapsed_precise}/{eta_precise}]").unwrap();

        (0..num_games)
            .into_par_iter()
            .progress_count(num_games as u64)
            .with_style(style)
            .for_each(|_| {
                let winner = simulate(num_players, starting_money);
                wins.lock().unwrap()[winner] += 1;
            });
    } else {
        (0..num_games)
            .into_par_iter()
            .for_each(|_| {
                let winner = simulate(num_players, starting_money);
                wins.lock().unwrap()[winner] += 1;
            });
    }

    wins.lock().unwrap().clone()
}

/// Simulates a number of games and tallies the win counts of each player.
fn simulate(num_players: usize, starting_money: u32) -> usize {
    let mut players = vec![starting_money; num_players];
    let mut rng = rand::rng();

    let mut total_remaining_money = starting_money * num_players as u32;

    loop {
        for player_turn in 0..num_players {
            for _ in 0..(std::cmp::min(players[player_turn], 3)) {
                if total_remaining_money == players[player_turn] {
                    return player_turn;
                }

                let roll = rng.random_range(0..6);
                match roll {
                    0..3 => {}, // Dot - safe!
                    3 => {
                        // L
                        if player_turn == 0 {
                            players[num_players - 1] += 1;
                        } else {
                            players[player_turn - 1] += 1;
                        }
                        players[player_turn] -= 1;
                    },
                    4 => {
                        // R
                        if player_turn == (num_players - 1) {
                            players[0] += 1;
                        } else {
                            players[player_turn + 1] += 1;
                        }
                        players[player_turn] -= 1;
                    },
                    5 => {
                        // C
                        players[player_turn] -= 1;
                        total_remaining_money -= 1;
                    },
                    _ => (),
                }
            }
        }
    }
}