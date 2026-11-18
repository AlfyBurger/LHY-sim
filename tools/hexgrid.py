"""Hex geometry of the GMT 'Vol. 1 Hidden Setup' sector images (3300x5100, portrait, row 1 at top).

Columns A..K are 330 px apart starting at x=0 (A and K are half hexes on the edges).
Odd columns (A, C, E, G, I, K) have centres at y = 195 + 392*(row-1);
even columns (B, D, F, H, J) at y = 391 + 392*(row-1).
Flat-topped hexes: vertices point left/right (west/east).
"""
COLS = "ABCDEFGHIJK"
DX, DY, Y0_ODD, Y0_EVEN = 330.0, 392.0, 195.0, 391.0

def center(hexid: str):
    c = COLS.index(hexid[0]); r = int(hexid[1:])
    y0 = Y0_ODD if c % 2 == 0 else Y0_EVEN
    return (c * DX, y0 + (r - 1) * DY)

def all_hexes(rows=13):
    out = []
    for c, L in enumerate(COLS):
        maxr = rows
        for r in range(1, maxr + 1):
            x, y = center(f"{L}{r}")
            if y <= 5100 + 1:
                out.append(f"{L}{r}")
    return out

def neighbours(hexid: str):
    """Six neighbours in order N, NE, SE, S, SW, NW (ids may be off-map)."""
    c = COLS.index(hexid[0]); r = int(hexid[1:])
    odd = (c % 2 == 0)  # columns A, C, ... sit higher
    def h(cc, rr):
        return f"{COLS[cc]}{rr}" if 0 <= cc < len(COLS) and rr >= 1 else None
    if odd:
        return [h(c, r-1), h(c+1, r-1), h(c+1, r), h(c, r+1), h(c-1, r), h(c-1, r-1)]
    return [h(c, r-1), h(c+1, r), h(c+1, r+1), h(c, r+1), h(c-1, r+1), h(c-1, r)]
