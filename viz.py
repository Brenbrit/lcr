#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pillow>=10",
# ]
# ///

IMAGE_SIZE = 4096 # pixels, both x and y
IMAGE_BACKGROUND_COLOR = (255, 255, 255, 0) # RGBA

# The number of empty pixels to put on each side of circle.
BIG_CIRCLE_BUFFER = 500 # pixels

# The percentage of each slice to show.
# If set to 0.1, only the crust is visible.
SLICE_VISIBLE_PCT = 0.20

FONT_SIZE = 72

# Colors!
BEST_COLOR = (0, 255, 0)
WORST_COLOR = (255, 0, 0)

# Circle-related functions
from math import cos, radians, sin
# Image creation and manipulation
from PIL import Image, ImageDraw, ImageFont
# Input reading
from sys import argv, stdin

# Given a minimum color (say red) and a maximum color (say green),
# create an srgb-interpolated color based on a 0-1 percentage.
def interp_srgb(min_color: tuple[int, int, int], max_color: tuple[int, int, int], percentage: float) -> tuple[int, int, int]:
    min_r, min_g, min_b = min_color
    max_r, max_g, max_b = max_color
    
    diff_r = max_r - min_r
    diff_g = max_g - min_g
    diff_b = max_b - min_b

    return (min_r + int(diff_r * percentage), min_g + int(diff_g * percentage), min_b + int(diff_b * percentage))

# Utility function that finds the center of a given player's pie slice, in degrees.
def get_slice_center(num_players: int, player_num: int) -> float:
    base_circle_deg_per_player = 360 / num_players
    return -90 + (player_num * base_circle_deg_per_player)

# Given a list of win percentages and a file, write a visualization of each player's
# win percentage to the file.
def draw_position_heat_map(players: list[float], image_save_location: str) -> None:
    # Create the image with alpha
    im = Image.new('RGBA', (IMAGE_SIZE, IMAGE_SIZE), IMAGE_BACKGROUND_COLOR)
    draw = ImageDraw.Draw(im)

    # Calculate some info about the circle we'll draw
    big_circle_start = BIG_CIRCLE_BUFFER # both x and y pixels
    big_circle_end = IMAGE_SIZE - BIG_CIRCLE_BUFFER # both x and y pixels
    big_circle_shape = [(big_circle_start, big_circle_start), (big_circle_end, big_circle_end)]

    # Calculate some info related to drawing degrees
    num_players = len(players)
    base_circle_deg_per_player = 360 / num_players
    buffer_deg = int((360 / num_players) / 7.5)
    rotation_amount = int(-90 - (base_circle_deg_per_player / 2) - (buffer_deg / 2))

    # Used to figure out which color to draw
    min_win_pct = min(players)
    win_pct_range = max(players) - min_win_pct

    # Draw the pie slice for each player
    for player_num in range(num_players):
        # The center of this player's color, in degrees
        player_circle_position_center = get_slice_center(num_players, player_num)
        # The exact degrees to start/stop drawing this player's slice
        circle_start = player_circle_position_center - (base_circle_deg_per_player / 2) + buffer_deg
        circle_end = player_circle_position_center + (base_circle_deg_per_player / 2) - buffer_deg

        # The percent you would like to sit here ;)
        interp_pct = (players[player_num] - min_win_pct) / win_pct_range

        draw.pieslice(big_circle_shape, start = circle_start, end = circle_end, fill = interp_srgb(WORST_COLOR, BEST_COLOR, interp_pct))

    # Draw a smaller circle above the big one to make each player more trapezoid-like
    big_circle_radius = (IMAGE_SIZE - int(BIG_CIRCLE_BUFFER / 2)) / 2
    # The number of pixels in from each side to draw the smaller circle
    smaller_circle_diff = big_circle_radius * SLICE_VISIBLE_PCT
    smaller_circle_shape = [(big_circle_start + smaller_circle_diff, big_circle_start + smaller_circle_diff), (big_circle_end - smaller_circle_diff, big_circle_end - smaller_circle_diff)]
    draw.pieslice(smaller_circle_shape, start = 0, end = 360, fill = IMAGE_BACKGROUND_COLOR)

    # Draw text inside each pie slice
    circle_center = (big_circle_start + big_circle_end) / 2
    circle_radius = (big_circle_end - big_circle_start) / 2
    # The percentage through the radius to draw text
    # We subtract that little bit at the end to improve visuals a little bit
    pct_radius_to_draw_text = 1 - (SLICE_VISIBLE_PCT / 2) - 0.02
    # The font to use
    font = ImageFont.load_default(size = FONT_SIZE)

    for player_num in range(num_players):
        # Get the text to draw
        player_win_pct_above_mean = players[player_num] - (1 / num_players)
        player_win_pct_above_mean_str = f"{player_win_pct_above_mean * 100:.1f}"
        # Add a + to the above-mean win percent if applicable
        if player_win_pct_above_mean > 0:
            player_win_pct_above_mean_str = "+" + player_win_pct_above_mean_str

        text_to_draw = f"P{player_num}\nWR {players[player_num] * 100:.1f}%\n({player_win_pct_above_mean_str}%)"

        # Find where we want the center of our text to be
        pie_slice_center_degrees = get_slice_center(num_players, player_num)
        draw_point_x = circle_center + (circle_radius * cos(radians(pie_slice_center_degrees)) * pct_radius_to_draw_text)
        draw_point_y = circle_center + (circle_radius * sin(radians(pie_slice_center_degrees)) * pct_radius_to_draw_text)

        # Move the text around a little based on how tall/wide it is
        (bbox_left, bbox_top, bbox_right, bbox_bottom) = draw.multiline_textbbox((draw_point_x, draw_point_y), text = text_to_draw, font = font, align='center')
        text_based_offset_x = -1 * (bbox_right - bbox_left) / 2
        text_based_offset_y = -1 * (bbox_bottom - bbox_top) / 2

        draw.multiline_text((draw_point_x + text_based_offset_x, draw_point_y + text_based_offset_y), text_to_draw, font = font, align='center', fill = 'black')


    im.save(image_save_location)

if __name__ == "__main__":

    win_counts = []
    for line in stdin:
        win_counts.append(int(line))

    draw_position_heat_map([i / sum(win_counts) for i in win_counts], argv[1])