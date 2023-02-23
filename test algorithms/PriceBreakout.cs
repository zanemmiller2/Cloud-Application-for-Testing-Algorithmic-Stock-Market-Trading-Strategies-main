using QuantConnect.Data;
using QuantConnect.Data.Market;
using QuantConnect.Indicators;
using QuantConnect.Orders;
using QuantConnect.Orders.Fees;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace QuantConnect.Algorithm.CSharp
{
    public class PriceBreakout:QCAlgorithm
    {
        //Input data file
        private string _symbol = "TQQQ";
        const int def_start_date_year = 2011;
        const int def_start_date_month = 1;
        const int def_start_date_day = 1;
        const int def_end_date_year = 2021;
        const int def_end_date_month = 12;
        const int def_end_date_day = 31;


        //Algorithm Parameters---------------------------------------
        public int HullPeriod { get; set; } = 50;
        public int AverageTrueRangePeriod { get; set; } = 60;
        public int BuyLag { get; set; } = 6;
        public decimal RangeStopLossMultiple { get; set; } = 2.5m;
        public decimal ChannelStopLossMultiple { get; set; } = .97m;
        //--------------------------------------------------------------

        //Internal objects and variables 
        private AverageTrueRange averageTrueRange;
        private TrueRange trueRange;
        private HullMovingAverage hullHigh;
        private HullMovingAverage hullLow;

        private decimal buyPrice;
        private bool buyPatternComplete;
        private bool buyDelayComplete;
        private int buyDaysCount;
        private decimal tradeHigh;
        private decimal stopLoss;
        private bool changed;


        public PriceBreakout()
        {
        }

        public override void Initialize()
        {

            var start_date_year = GetParameter("start_date_year", def_start_date_year);
            var start_date_month = GetParameter("start_date_month", def_start_date_month);
            var start_date_day = GetParameter("start_date_day", def_start_date_day);

            var end_date_year = GetParameter("end_date_year", def_end_date_year);
            var end_date_month = GetParameter("end_date_month", def_end_date_day);
            var end_date_day = GetParameter("end_date_day", def_end_date_day);
            var ticker = GetParameter("ticker", _symbol);

            SetSecurityInitializer(security => security.FeeModel = new ConstantFeeModel(0));
            AddSecurity(SecurityType.Equity, ticker, Resolution.Daily);

            SetStartDate(start_date_year, start_date_month, start_date_day); // Set Start Date
            SetEndDate(end_date_year, end_date_month, end_date_day); // Set Start Date
            SetCash(100000);             //Set Strategy
            SetWarmUp(TimeSpan.FromDays(350), Resolution.Daily);
            SetWarmup(100);

            averageTrueRange = ATR(ticker, AverageTrueRangePeriod, MovingAverageType.Hull);
            trueRange = TR(ticker);

            hullHigh = HMA(ticker, HullPeriod, Resolution.Daily, x => ((TradeBar)x).High);
            hullLow = HMA(ticker, HullPeriod, Resolution.Daily, x => ((TradeBar)x).Low);

            tradeHigh = 0.0m;
            stopLoss = 0.0m;
            buyPrice = 0.0m;
            buyPatternComplete = false;
            buyDelayComplete = false;
        }

        /// <summary>
        /// OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        /// </summary>
        /// <param name="data">Slice object keyed by symbol containing the stock data</param>
        public override void OnData(Slice slice)
        {
            var ticker = GetParameter("ticker", _symbol);
            if (IsWarmingUp) return;

            if (!hullHigh.IsReady) return;
            if (!averageTrueRange.IsReady) return;
            if (!hullHigh.IsReady) return;

            TradeBar bar = slice.Bars[ticker];
            changed = false;

            // Buy pattern and buy delay-----------------------------------------------------------------------------------------

            // Check if the buy pattern and buy delay both complete 
            if (buyPatternComplete)
            {
                buyDaysCount++;
            }
            if (trueRange > averageTrueRange && bar.Close > hullHigh && !buyPatternComplete)
            {
                buyPatternComplete = true;
            }
            if (buyPatternComplete && !buyDelayComplete && buyDaysCount == BuyLag)
            {
                buyDelayComplete = true;
            }

            //Calculate a stop loss value
            if (bar.High > tradeHigh && Portfolio.Invested)  
            {
                tradeHigh = bar.High;
                stopLoss = tradeHigh - RangeStopLossMultiple * averageTrueRange.Current.Value;
            }

            // Buy signal-------------------------------------------------------------------------------------
            if (buyPatternComplete && buyDelayComplete && !Portfolio.Invested)  
            {
                changed = true;
                buyPatternComplete = false;
                buyDelayComplete = false;
                buyDaysCount = 0;
            }

            // Trailing stop loss------------------------------------------------------------------------------
            else if (bar.Close < stopLoss && Portfolio.Invested) 
            {
                changed = true;
                tradeHigh = 0.0m;
                stopLoss = 0.0m;
            }

            //Price channel stop loss--------------------------------------------------------------------------- 
            else if (bar.Close < (ChannelStopLossMultiple * hullLow.Current.Value) && Portfolio.Invested) 
            {
                changed = true;
                tradeHigh = 0.0m;
                stopLoss = 0.0m;
            }

            // Fixed stop loss in case of disaster-------------------------------------------------------------
            if (Securities[ticker].Close < buyPrice * .90m)
            {
                changed = true;
                tradeHigh = 0.0m;
                stopLoss = 0.0m;
            }

            // Execute the buy and sell orders-------------------------------------------------------------------
            if (changed)
            {
                double percentage;
                //Sell
                if (Portfolio.Invested) percentage = 0;
                //Buy
                else percentage = 1;

                // submit order
                SetHoldings(ticker, percentage);
            }
        }
        public override void OnOrderEvent(OrderEvent orderEvent)
        {
            if (orderEvent.Status == OrderStatus.Filled)
            {
                if (orderEvent.Direction == OrderDirection.Buy)
                    buyPrice = orderEvent.FillPrice;
                else
                    buyPrice = 0;
                Log($"{orderEvent}");
            }
        }
    }
}

