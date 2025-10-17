# Moltenprot data pre-processing
This repo contains a simple script to clip messy ends from Moltenprot inputs based on the shape of the first derivative. The clipping uses two characteristics: first, it clips anything after the first derivative becomes negative and then returns to positive (may be the first or second of these transitions, depending on whether the first derivative is negative or positive to begin with); second, it clips ends where the first derivative has dipped or jumped more than 0.025 above 0. Combined, these two thresholds successfully clip the curves present in the sample dataset provided in the `data` directory. The script saves before and after pltos of the ratios and first derivatives for each curve, as different data may not conform to these expectations; be sure to check your plots to see that these assumptions hold for your data. Examples of these plots and the resulting excel file are included in the sample `data` directory.

The only packages you need to have in order to run this code are `pandas`, `numpy`, and `matplotlib`.

An example of how to run this script from the `scripts` directory using the sample data in `data`:

```
python clip_moltenprot.py ../data/02-07-2025_Prometheus-processed_data-unchanged.xlsx ../data/ 17Oct2025
```