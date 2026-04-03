from sub_analysis.cleaning_validation import clean_data
from sub_analysis.metric_calculation import calculate_metrics
from sub_analysis.profitability_analysis import aggregate_product_metrics, product_identify
from sub_analysis.div_performance import division_performance, identify_divisions 
from sub_analysis.pareto_analysis import pareto_profit_analysis
from sub_analysis.cost_analysis import cost_structure_analysis, flag_product_cost_issues
from sub_analysis.kpi_analysis import calculate_kpis, margin_volatility

import pandas as pd

def main():

    # load csv ONLY HERE
    df = pd.read_csv("data/Nassau_Candy_Distributor.csv")

    # clean
    df = clean_data(df)

    # metrics
    df = calculate_metrics(df)

    # product summary
    product_summary = aggregate_product_metrics(df)

    # identify category
    product_summary = product_identify(product_summary)

    print("\nCleaned Data:")
    print(df.head(10).to_string())

    print("\nProduct Summary:")
    print(product_summary.head(20).to_string())

    # division performance
    division_summary = division_performance(df)
    division_summary = identify_divisions(division_summary)
    print("\nDivision Summary:")
    print(division_summary.to_string())

    # pareto analysis
    product_summary = pareto_profit_analysis(product_summary)
    print("\nProduct Summary with Pareto Analysis:")
    print(product_summary.to_string())

    # cost analysis
    product_summary = cost_structure_analysis(product_summary)
    product_summary = flag_product_cost_issues(product_summary)
    print("\nProduct Summary with Cost Analysis:")
    print(product_summary.to_string())


  # KPI calculation
    kpi_df = calculate_kpis(df)

    print("\n===== KPI DATA =====")
    print(kpi_df.head(20).to_string())

    # margin volatility
    volatility_df = margin_volatility(kpi_df)

    print("\n===== MARGIN VOLATILITY =====")
    print(volatility_df.to_string())

  # ================= SAVE FINAL DASHBOARD DATA =================

    with pd.ExcelWriter("nassau_candy_analysis.xlsx", engine="openpyxl") as writer:
      product_summary.to_excel(writer, sheet_name="Product_Summary", index=False)
      division_summary.to_excel(writer, sheet_name="Division_Summary", index=False)
      kpi_df.to_excel(writer, sheet_name="KPI_Data", index=False)
      volatility_df.to_excel(writer, sheet_name="Margin_Volatility", index=False)

print("\n✅ FINAL DASHBOARD FILE CREATED: nassau_candy_analysis.xlsx")
    
if __name__ == "__main__":
    main()





    

