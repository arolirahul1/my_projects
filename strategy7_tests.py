
import unittest
from new1 import user_transactions, Strategy7

class Test_strategy7(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        user_data = {'balance': 10000, 'userid': 1, 'max_loss_perc_pd': 1, 'max_profit_perc_pd': 1}
        self.ut = user_transactions(user_data)
        self.strategy7 = Strategy7(user_data)

    def _test_is_max_loss_profit(self):
        ut = self.ut
        ut.list_pnl = [-100]
        self.assertTrue(ut.is_max_loss_reached(), 'max loss not reached')
        ut.list_pnl = [-99]
        self.assertFalse(ut.is_max_profit_reached(), 'max loss reached')
        ut.list_pnl = [100]
        self.assertTrue(ut.is_max_profit_reached(), 'max profit reached')
        ut.list_pnl = [99]
        self.assertFalse(ut.is_max_profit_reached(), 'max profit not reached')

    def _test_is_buy(self,preference=2):
        self.ut.list_pnl = [] #Reset the pnl
        is_buy_val = self.strategy7.is_buy({'trend':'up',"open":101,'lbb': 102, 'ubb': 109, 'close': 103},)
        self.assertTrue(is_buy_val, 'Its not a valid buy')

    def test_is_sell(self,preference=2):
        self.strategy7.Buy({'trend':'up',"open":101,'lbb': 102, 'ubb': 109, 'close': 103})
        self.ut.list_pnl = [] #Reset the pnl
        is_sell_val = self.strategy7.is_sell({'trend':'down',"open":102,'lbb': 103, 'ubb': 120, 'close':150},)
        self.assertFalse(is_sell_val, 'Its not a valid sell')

    def test_buy_rank(self):
        buying_rank=self.strategy7.buy_rank({"trend":"up","open":101,"close":103,"ubb":109,"lbb":102})
        self.assertTrue(buying_rank,"rank > 0")

    def test_sell_rank(self):
        selling_rank=self.strategy7.sell_rank({"trend":"down","open":99,"close":130,"ubb":120,"lbb":103})
        self.assertTrue(selling_rank,"rank > 0")

    def test_is_morethan_range(self):
        self.assertTrue(self.strategy7.is_morethan_range(100, 99.1))
        self.assertTrue(self.strategy7.is_morethan_range(100, 105))
        self.assertFalse(self.strategy7.is_morethan_range(100, 98.9))

    def test_is_lessthan_range(self):
        self.assertTrue(self.strategy7.is_lessthan_range(100, 101))
        self.assertTrue(self.strategy7.is_lessthan_range(100, 94))
        self.assertFalse(self.strategy7.is_lessthan_range(100, 101.1))

if __name__ == '__main__':
    unittest.main()
