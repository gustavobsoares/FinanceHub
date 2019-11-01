import pandas as pd
from datetime import date
from calendars import DayCounts


class B3AbstractDerivative(object):

    monthdict = {'F': 1, 'G': 2, 'H': 3, 'J':  4, 'K':  5, 'M':  6,
                 'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}

    calendar = None
    contract = None
    dc_convention = None
    pilar_day = None
    roll_method = None

    def __init__(self, db_connect):
        self.conn = db_connect
        self.time_series = self._get_time_series()
        self.dc = DayCounts(dc=self.dc_convention, calendar=self.calendar)

    def time_menu(self, code=None):
        """
        Gets all of the available trading dates for the contract in 'code'.
        If 'code' is None, all dates are returned.
        :param code: str with the contract code
        :return: list of timestamps
        """
        if code is None:
            tm = self.time_series.index.levels[0]
        else:
            tm = self.time_series.index.get_loc_level(code, 1)[1]

        return list(tm)

    def market_menu(self, t=None):
        """
        Gets all of the available contracts codes for date 't'.
        If 't' is None, all contract codes are returned.
        :param t: any format accepted by pandas.to_datetime()
        :return: list of timestamps
        """
        if t is None:
            mm = self.time_series.index.levels[1]
        else:
            t = pd.to_datetime(t)
            mm = self.time_series.index.get_loc_level(t, 0)[1]

        return list(mm)

    def maturity(self, code):
        """
        Given a contract code, returns the timestamp of the maturity date.
        THIS FUNCTION WILL BREAK WHEN CONTRACTS MATURE IN 2092 START TRADING
        :param code: str with contract code
        :return: tuple (year, month)
        """
        month = self.monthdict[code.upper()[0]]
        year = int(code.upper()[1:])

        if year >= 92:
            year = year + 1900
        else:
            year = year + 2000

        mat_date = date(year, month, self.pilar_day)
        mat_date = self.dc.busdateroll(mat_date, self.roll_method)
        return mat_date

    def du2maturity(self, t, code):
        """
        returns the number of business days between t and the maturity date of the contract
        :param t: current date
        :param code: contract code
        :return: int
        """
        mat_date = self.maturity(code)
        du = self.dc.days(t, mat_date)
        return du

    def dc2maturity(self, t, code):
        """
        returns the number of actual days between t and the maturity date of the contract, independent
        of the daycount convention
        :param t: current date
        :param code: contract code
        :return: int
        """
        mat_date = self.maturity(code)
        du = self.dc.daysnodc(t, mat_date)
        return du

    def volume(self, code, t=None):
        """
        returns the trading volume. If 't' is None, returns a pandas Series of the volume of 'code'.
        """
        if t is None:
            filter_contract = self.time_series.index.get_loc_level(code, 1)[0]
            v = self.time_series[filter_contract]['trading_volume'].droplevel(1)
        else:
            v = self.time_series['trading_volume'].loc[t, code]

        return v

    def open_interest(self, code, t=None):
        """
        returns the open interest at the close of date 't'.
        If 't' is None, returns a pandas Series of the volume of 'code'.
        """
        if t is None:
            filter_contract = self.time_series.index.get_loc_level(code, 1)[0]
            v = self.time_series[filter_contract]['open_interest_close'].droplevel(1)
        else:
            v = self.time_series['open_interest_close'].loc[t, code]

        return v

    def pnl(self):
        # TODO implement
        pass

    def build_df(self):
        # TODO implement
        df = self.time_series.reset_index([0, 1])
        return

    def filter(self):
        # TODO implement
        pass

    def _get_time_series(self):

        sql_query = self._time_series_query()

        df = pd.read_sql(sql=sql_query,
                         con=self.conn,
                         parse_dates={'time_stamp': '%Y-%m-%d'})

        df = df.set_index(['time_stamp', 'maturity_code'])

        return df

    def _time_series_query(self):
        path = r'query_b3_timeseries.sql'

        with open(path, 'r') as file:
            sql_query = file.read() % {'name': self.contract}

        return sql_query


class DI1(B3AbstractDerivative):
    calendar = 'anbima'
    contract = 'DI1'
    dc_convention = 'BUS/252'
    pilar_day = 1
    roll_method = 'forward'

    def implied_yield(self):
        pass

    def theoretical_price(self):
        pass

    def duration(self):
        pass

    def modified_duration(self):
        pass

    def dv01(self):
        pass
