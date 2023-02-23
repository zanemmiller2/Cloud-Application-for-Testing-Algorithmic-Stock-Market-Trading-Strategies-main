using QuantConnect.Data;

namespace QuantConnect.Algorithm.CSharp
{
    public class Testcsharp : QCAlgorithm
    {
        const int def_start_date_year = 2011;
        const int def_start_date_month = 1;
        const int def_start_date_day = 1;
        const int def_end_date_year = 2021;
        const int def_end_date_month = 12;
        const int def_end_date_day = 31;
        const string def_ticker = "SPY";

        public override void Initialize()
        {
            var start_date_year = GetParameter("start_date_year", def_start_date_year);
            var start_date_month = GetParameter("start_date_month", def_start_date_month);
            var start_date_day = GetParameter("start_date_day", def_start_date_day);

            var end_date_year = GetParameter("end_date_year", def_end_date_year);
            var end_date_month = GetParameter("end_date_month", def_end_date_day);
            var end_date_day = GetParameter("end_date_day", def_end_date_day);
            var ticker = GetParameter("ticker", def_ticker);

            SetStartDate(start_date_year, start_date_month, start_date_day); // Set Start Date
            SetEndDate(end_date_year, end_date_month, end_date_day); // Set Start Date
            SetCash(100000); // Set Strategy Cash
            AddEquity(ticker, Resolution.Daily);
        }

        /// OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        /// Slice object keyed by symbol containing the stock data
        public override void OnData(Slice data)
        {
            var ticker = GetParameter("ticker", def_ticker);
            if (!Portfolio.Invested)
            {
                SetHoldings(ticker, 1);
                Debug("Purchased Stock");
            }
        }
    }
}
