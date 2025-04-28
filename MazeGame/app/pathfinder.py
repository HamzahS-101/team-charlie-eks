from collections import deque


def is_valid(grid, visited, row, col):
    # Check if (row, col) is a valid position
    return (
        0 <= row < len(grid)
        and 0 <= col < len(grid[0])
        and not grid[row][col]
        and not visited[row][col]
    )


def bfs(grid, start, end):
    # start and end are in format (y, x) or (row, col)

    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Initialize visited matrix and parent map
    visited = []
    for row in range(len(grid)):
        visited.append([])
        for _ in range(len(grid[0])):
            visited[row].append(False)

    if not (0 <= start[0] < len(grid) or 0 <= start[1] < len(grid[0])):
        return []

    parent = {}

    # Queue for BFS: stores (row, col) tuples
    queue = deque([start])
    # print(start[0], start[1])
    try:
        visited[start[0]][start[1]] = True
    except IndexError:
        print(start)
        print(len(visited), len(visited[0]))
        raise

    while queue:
        row, col = queue.popleft()

        # Check if the end is reached
        if (row, col) == end:
            path = []
            while (row, col) != start:
                path.append((row, col))
                row, col = parent[(row, col)]
            path.append(start)
            return path[::-1]  # Reverse the path

        # Explore neighbors
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if is_valid(grid, visited, r, c):
                visited[r][c] = True
                parent[(r, c)] = (row, col)
                queue.append((r, c))

    return []  # Path not found
