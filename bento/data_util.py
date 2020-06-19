import pandas as pd
from iso3166 import countries


def pad_choropleth(data):
    fdf = data["df"]
    zeros = {key: 0 for key in data["columns"]}
    padded_data = []
    for entry in countries:
        if entry.alpha3 not in fdf.alpha3.unique():
            padded_data.append(
                {
                    **zeros,
                    "Date": fdf.Date.max(),
                    "Country": entry.apolitical_name,
                    "alpha3": entry.alpha3,
                }
            )

    pdf = fdf[fdf.Date == fdf.Date.max()]
    pdf = pd.concat([pdf, pd.DataFrame(padded_data)], sort=True)
    return pdf
