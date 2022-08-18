# Jackaroo

Requries Python ver. >= 3.7

Windows:

```bash
    py -m venv venv
    pip install -r requirements.txt
```

UNIX:

```bash
    python3 -m venv venv
    pip install -r requirements.txt
```

# Rules

## Specials

- (1 / Ace) Three options: Free one marble from jail or move 1 or 11 steps
- (4) Move backwards 4 steps
- (5) Move any marble on the board 5 steps (Excludes marbles other than your own in their home bases)
- (7) Split 7 steps over two of your own marbles. (Includes 7-0 and 0-7)
- (10) Next player discards a card of your choice (Without you looking at the cards) or move ten spaces
- (11) Swap with any other marble on the board. (Excludes own marbles and marbles in their home base)
- (13) Free one marble from jail or move your marble 13 steps and eat all the marbles in path.

## Regulars

- (2)  Move 2 steps
- (3)  Move 3 steps
- (6)  Move 6 steps
- (8)  Move 8 steps
- (9)  Move 9 steps
- (12) Move 12 steps

