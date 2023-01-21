class game:
    def tic_tac_toe_blocker(self, num1, num2):
        positions = [1, 2, 3, 4, 5, 6, 7, 8]
        wining_comb = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 5, 9], [3, 5, 7]]
        if num1 in positions and num2 in positions:
            for i in wining_comb:
                if num1 in i and num2 in i:
                    difference = set(i).difference({num1, num2})
                    break
        return difference

    def tic_tac_toe_blocker2(self, player1_positions, player2_positions):
        board = [0, 1, 2,
                 3, 4, 5,
                 6, 7, 8]
        wining_comb = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                       [0, 3, 6], [1, 4, 7], [2, 5, 8],
                       [0, 4, 8], [2, 4, 6]]
        for combination in wining_comb:
            count = 0
            for pos in combination:
                if pos in player2_positions:
                    count += 1
            if count == 2:
                remaining_pos = set(combination).difference(player2_positions)
                if not remaining_pos.issubset(player1_positions):
                    return remaining_pos.pop()
        return board[0]

if __name__ == "__main__":
    block=game().tic_tac_toe_blocker2([1,2],[2,0])
    print(block)

