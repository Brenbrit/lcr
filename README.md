# LCR
Brendan's [LCR](https://www.georgeandcompany.co/products/lcr-dice-game) simulator and visualizer.

## Requirements
- [uv](https://docs.astral.sh/uv/) (optional)

## Building
```
(lcr-sim) $ cargo build --release
```

## Usage
### Run a simulation
```
(lcr-sim) $ target/release/lcr-sim --players 10 --games 1000
```
### Run a simulation and make a pretty picture
```
(lcr) $ lcr-sim/target/release/lcr-sim --players 10 --games 1000 -s | ./viz.py results.png
(lcr) $ xdg-open results.png
```
### Get the best position for a given player count
```
(lcr) ./best_position.py <num players>
```
- Note that the default player count is 100M. This takes ~45s on my Ryzen 7800X3D. You can change `NUM_GAMES` in the shell script if you'd like to change the game count.

## Notes
- Except for turn order, LCR is a pure-luck game. This means you should probably simulate many more games than I've shown in the examples above (I recomment at least 10 million).
- `lcr-sim` is a multithreaded Rust (insert rocketship emoji) program because running 10 million game simulations is slow. If you find some optimization I missed, feel free to PR!
- `viz.py` is a `uv` and [PEP 728](https://peps.python.org/pep-0723/)-enabled script. This is why I put `uv` in the requirements section. If you don't have `uv`, you can still run the script by installing `pillow>=10` and running with `python viz.py`.